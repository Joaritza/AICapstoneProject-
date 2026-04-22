"""Basic tests for ingredient tools."""

import pytest
from tools.ingredient_tools import check_ingredient_vegan_status, get_vegan_alternatives
from utils.exceptions import IngredientNotFoundError, ValidationError


def test_check_ingredient_vegan_status_vegan():
    """Test checking vegan status of a vegan ingredient."""
    result = check_ingredient_vegan_status("tofu")
    
    assert result is not None
    assert result["vegan"] == True
    assert "Local Vegan Database" in result["sources"]
    assert result["name"] == "Tofu"


def test_check_ingredient_vegan_status_non_vegan():
    """Test checking vegan status of a non-vegan ingredient."""
    result = check_ingredient_vegan_status("milk")
    
    assert result is not None
    assert result["vegan"] == False
    assert "Local Vegan Database" in result["sources"]
    assert "Soy Milk" in result["alternatives"] or len(result["alternatives"]) > 0


def test_check_ingredient_invalid_input():
    """Test with invalid ingredient name."""
    with pytest.raises(ValidationError):
        check_ingredient_vegan_status("")


def test_get_vegan_alternatives_for_non_vegan():
    """Test getting alternatives for non-vegan ingredient."""
    alts = get_vegan_alternatives("milk", limit=3)
    
    assert isinstance(alts, list)
    assert len(alts) > 0
    assert "alternative" in alts[0]


def test_get_vegan_alternatives_for_vegan():
    """Test getting alternatives for vegan ingredient."""
    alts = get_vegan_alternatives("tofu", limit=3)
    
    assert isinstance(alts, list)
    assert alts[0]["alternative"] == "Tofu"
    assert "already vegan" in alts[0]["reason"].lower()


if __name__ == "__main__":
    # Run basic tests
    print("Testing vegan ingredient database...")
    
    try:
        result = check_ingredient_vegan_status("milk")
        print(f"✓ Milk check: {result['vegan']} ({result['sources']})")
    except Exception as e:
        print(f"✗ Milk check failed: {e}")
    
    try:
        result = check_ingredient_vegan_status("tofu")
        print(f"✓ Tofu check: {result['vegan']} ({result['sources']})")
    except Exception as e:
        print(f"✗ Tofu check failed: {e}")
    
    try:
        alts = get_vegan_alternatives("milk", limit=3)
        print(f"✓ Milk alternatives: {len(alts)} found")
    except Exception as e:
        print(f"✗ Milk alternatives failed: {e}")
    
    print("\nAll basic tests completed!")
