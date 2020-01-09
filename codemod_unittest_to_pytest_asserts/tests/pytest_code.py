import pytest
class ExampleTest:
    def test_something(self):
        assert 1 == 1
        assert 1 == 1, '1 should always be 1'
        assert 1 == 1, '1 should always be 1'
        assert 1 == 1
        # 1 should always be one

        def inner_test_method():
            assert 1 == 1
            with pytest.raises(ValueError):
                raise ValueError("SomeError")

        innerTestMethod()

        assert 1 == 1

    def test_lots_of_arguments(self):
        def inside_another_function():

            assert get_product_from_backend_product_with_supplier_product_and_cart_etc_etc_etc(product__backend_product_id=self.backend_product.id, product_id=self.product.id, name='Julebrus') is True
            assert True

        assert not False
