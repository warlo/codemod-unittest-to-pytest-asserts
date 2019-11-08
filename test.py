class ExampleTest:
    def test_something():
        self.assertEqual(1, 1)
        self.assertEqual(1, 1, msg="1 should always be 1")
        self.assertEqual(1, 1, "1 should always be 1")

        def inner_test_method():
            self.assertEqual(1, 1)

        inner_test_method()

        self.assertEqual(1, 1)
