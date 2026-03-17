"""
Focused Test Suite for E-commerce Product Quality Checker
Tests for: Agents, Main, Nodes, Graph, and Workflow
10-15 Test Cases
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any


# Import modules to test
from state import ProductData, ProductQualityState, create_initial_state
from agents.description_agent import DescriptionQualityAgent
from agents.pricing_agent import PricingValidatorAgent
from analyzer.quality_analyzer import QualityAnalyzer
from workflow.workflow_manager import WorkflowManager
from graph import WorkflowExecutor, create_quality_check_graph, get_workflow_description
from nodes.validation_node import validation_node
from nodes.agent_execution_node import agent_execution_node
from main import load_sample_product, initialize_system




# ============================================================================
# Mock Data Fixtures
# ============================================================================


@pytest.fixture
def valid_product() -> ProductData:
    """Valid product data for testing"""
    return {
        'product_id': 'TEST-001',
        'title': 'Premium Wireless Headphones',
        'description': 'High-quality wireless headphones with active noise cancellation',
        'price': 149.99,
        'category': 'Electronics',
        'images': [
            'https://8080-fdabebedaabeaddcfa343872981eecebfccaebdfone.premiumproject.examly.io/image1.jpg',
            'https://8080-fdabebedaabeaddcfa343872981eecebfccaebdfone.premiumproject.examly.io/image2.jpg',
            'https://8080-fdabebedaabeaddcfa343872981eecebfccaebdfone.premiumproject.examly.io/image3.jpg'
        ],
        'specifications': {
            'Battery': '30 hours',
            'Bluetooth': '5.0'
        },
        'reviews': [
            {'rating': 5, 'text': 'Excellent product!'},
            {'rating': 4, 'text': 'Very good quality'}
        ]
    }




@pytest.fixture
def invalid_product() -> ProductData:
    """Invalid product data for testing"""
    return {
        'product_id': '',
        'title': 'AB',
        'description': 'Short',
        'price': -10,
        'category': '',
        'images': [],
        'specifications': {},
        'reviews': []
    }




@pytest.fixture
def mock_gemini_service():
    """Mock Gemini service for testing"""
    mock_service = Mock()
    mock_service.analyze_with_structured_output = Mock(return_value={
        'score': 85.0,
        'status': 'passed',
        'issues': [],
        'suggestions': ['Consider adding more details'],
        'details': {}
    })
    return mock_service




@pytest.fixture
def quality_analyzer(mock_gemini_service):
    """Quality analyzer with mocked service"""
    return QualityAnalyzer(mock_gemini_service, use_llm=False)




@pytest.fixture
def workflow_manager(quality_analyzer):
    """Workflow manager for testing"""
    return WorkflowManager(quality_analyzer)




# ============================================================================
# Test Cases for Agents (2 tests)
# ============================================================================


def test_agent_description_quality_check(mock_gemini_service, valid_product):
    """Test Case 1: Test description agent quality check functionality"""
    agent = DescriptionQualityAgent(mock_gemini_service)
    result = agent.quick_check(valid_product)


    assert result['agent_name'] == 'Description Quality Agent'
    assert 'score' in result
    assert 'status' in result
    assert 'issues' in result
    assert 'suggestions' in result
    assert isinstance(result['score'], (int, float))




def test_agent_pricing_validation(mock_gemini_service, valid_product):
    """Test Case 2: Test pricing agent validation logic"""
    agent = PricingValidatorAgent(mock_gemini_service)
    result = agent.quick_check(valid_product)


    assert result['agent_name'] == 'Pricing Validator Agent'
    assert result['score'] > 0
    assert result['status'] in ['passed', 'warning', 'failed']
    assert result['details']['price'] == valid_product['price']
    assert result['details']['price_valid'] is True




# ============================================================================
# Test Cases for Main Module (3 tests)
# ============================================================================


def test_main_load_sample_product():
    """Test Case 3: Test loading sample product data from main module"""
    product = load_sample_product()


    assert 'product_id' in product
    assert 'title' in product
    assert 'description' in product
    assert 'price' in product
    assert product['price'] > 0
    assert len(product['images']) > 0




@patch('main.GeminiService')
def test_main_initialize_system(mock_gemini_class):
    """Test Case 4: Test system initialization from main module"""
    mock_service_instance = Mock()
    mock_gemini_class.return_value = mock_service_instance


    gemini_service, analyzer, workflow_mgr = initialize_system(
        api_key="test_key",
        use_llm=False
    )


    assert gemini_service is not None
    assert analyzer is not None
    assert workflow_mgr is not None
    assert isinstance(analyzer, QualityAnalyzer)
    assert isinstance(workflow_mgr, WorkflowManager)




def test_main_sample_product_structure():
    """Test Case 5: Test sample product has correct structure"""
    product = load_sample_product()


    required_fields = ['product_id', 'title', 'description', 'price',
                      'category', 'images', 'specifications', 'reviews']


    for field in required_fields:
        assert field in product, f"Missing required field: {field}"


    assert isinstance(product['price'], (int, float))
    assert isinstance(product['images'], list)
    assert isinstance(product['reviews'], list)




# ============================================================================
# Test Cases for Nodes (3 tests)
# ============================================================================


def test_node_validation_valid_product(valid_product):
    """Test Case 6: Test validation node with valid product"""
    state = create_initial_state(valid_product)
    updated_state = validation_node(state)


    assert updated_state['current_step'] == 'validation'
    assert updated_state['final_status'] != 'rejected'
    assert len(updated_state['errors']) == 0
    assert 'started_at' in updated_state['metadata']




def test_node_validation_invalid_product(invalid_product):
    """Test Case 7: Test validation node with invalid product"""
    state = create_initial_state(invalid_product)
    updated_state = validation_node(state)


    assert updated_state['current_step'] == 'validation'
    assert updated_state['final_status'] == 'rejected'
    assert len(updated_state['errors']) > 0
    assert any('Validation' in r['agent_name'] for r in updated_state['quality_results'])




def test_node_agent_execution(quality_analyzer, valid_product):
    """Test Case 8: Test agent execution node"""
    state = create_initial_state(valid_product)
    state['current_step'] = 'validation'
    updated_state = agent_execution_node(state, quality_analyzer)


    assert updated_state['current_step'] == 'agent_execution'
    assert len(updated_state['quality_results']) > 0
    assert updated_state['metadata']['total_checks'] > 0




# ============================================================================
# Test Cases for Graph (2 tests)
# ============================================================================


def test_graph_workflow_description():
    """Test Case 9: Test graph workflow description"""
    description = get_workflow_description()


    assert description['name'] == 'E-commerce Product Quality Check Workflow'
    assert 'steps' in description
    assert len(description['steps']) >= 4
    assert 'flow' in description
    assert 'validate' in description['flow']
    assert 'execute_agents' in description['flow']




def test_graph_workflow_executor_creation(quality_analyzer):
    """Test Case 10: Test graph workflow executor creation"""
    executor = WorkflowExecutor(quality_analyzer)


    assert executor.analyzer is not None
    assert executor.graph is not None
    assert hasattr(executor, 'execute')
    assert hasattr(executor, 'stream_execute')




# ============================================================================
# Test Cases for Workflow (5 tests)
# ============================================================================


def test_workflow_execute_complete_workflow(workflow_manager, valid_product):
    """Test Case 11: Test complete workflow execution"""
    result = workflow_manager.execute_workflow(valid_product, generate_report=True)


    assert 'state' in result
    assert 'analysis' in result
    assert 'reports' in result
    assert result['state']['final_status'] in ['approved', 'needs_review', 'rejected']
    assert 'text_report' in result['reports']
    assert 'json_report' in result['reports']




def test_workflow_quick_check(workflow_manager, valid_product):
    """Test Case 12: Test workflow quick check execution"""
    result = workflow_manager.execute_quick_check(valid_product)


    assert 'state' in result
    assert 'analysis' in result
    assert result['analysis']['overall_score'] >= 0
    assert result['analysis']['final_status'] in ['approved', 'needs_review', 'rejected']




def test_workflow_validation_only(workflow_manager, valid_product):
    """Test Case 13: Test workflow validation-only execution"""
    result = workflow_manager.validate_product_only(valid_product)


    assert 'valid' in result
    assert 'errors' in result
    assert 'status' in result
    assert result['valid'] is True
    assert len(result['errors']) == 0




def test_workflow_validation_only_invalid(workflow_manager, invalid_product):
    """Test Case 14: Test workflow validation-only with invalid product"""
    result = workflow_manager.validate_product_only(invalid_product)


    assert result['valid'] is False
    assert len(result['errors']) > 0
    assert result['status'] == 'rejected'




def test_workflow_get_status(workflow_manager, valid_product):
    """Test Case 15: Test workflow status retrieval"""
    state = create_initial_state(valid_product)
    state['current_step'] = 'validation'


    status = workflow_manager.get_workflow_status(state)
    assert status == 'validation'




# ============================================================================
# Run all tests
# ============================================================================


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])



