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
