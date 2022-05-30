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

    def test_assert_raises(self):
        with pytest.raises(ZeroDivisionError) as exc:
            divide_by_zero = 3 / 0
        assert exc.exception.args[0] == 'division by zero'

    def test_assert_raises_legacy(self):
        def foo():
            raise ValueError("bar")
        pytest.raises(ValueError, foo)

    def test_various_ops(self):
        assert 'a' in 'abc'
        assert 'a' not in 'def'
        assert 1 != 2
        assert None is None
        assert True is not False
        assert None is None
        assert True is not None
        assert isinstance(1, int)
        assert not isinstance(1, str)
        assert 1 < 2
        assert 2 <= 2
        assert 3 > 2
        assert 4 >= 3
