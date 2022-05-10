class ExampleTest:
    def test_something(self):
        self.assertEqual(1, 1)
        self.assertEqual(1, 1, msg="1 should always be 1")
        self.assertEqual(1, 1, "1 should always be 1")
        self.assertEqual(1, 1) # 1 should always be one

        def inner_test_method():
            self.assertEqual(1, 1)
            with self.assertRaises(ValueError):  # This error is always raised!
                raise ValueError("SomeError")

        innerTestMethod()

        self.assertEqual(1, 1)

    def test_lots_of_arguments(self):
        def inside_another_function():

            self.assertEqual(
                get_product_from_backend_product_with_supplier_product_and_cart_etc_etc_etc(
                    product__backend_product_id=self.backend_product.id,
                    product_id=self.product.id,
                    name="Julebrus",
                ),
                True
            )
            self.assertTrue(True)

        self.assertFalse(False)

    def test_assert_raises(self):
        with self.assertRaises(ZeroDivisionError) as exc:
            divide_by_zero = 3 / 0
        self.assertEqual(exc.exception.args[0], 'division by zero')

    def test_assert_raises_legacy(self):
        def foo():
            raise ValueError("bar")
        self.assertRaises(ValueError, foo)

    def test_various_ops(self):
        self.assertIn("a", "abc")
        self.assertNotIn("a", "def")
        self.assertNotEqual(1, 2)
        self.assertIs(None, None)
        self.assertIsNot(True, False)
        self.assertIsNone(None)
        self.assertIsNotNone(True)
        self.assertIsInstance(1, int)
        self.assertNotIsInstance(1, str)
        self.assertLess(1, 2)
        self.assertLessEqual(2, 2)
        self.assertGreater(3, 2)
        self.assertGreaterEqual(4, 3)

    def test_de_yoda(self):
        foo = "baz"
        self.assertEqual('bar', foo)
