@echo off
pytest tests/api/test_pet_crud_async.py tests/api/test_pet_negative_async.py --alluredir=reports/allure-results
allure generate reports/allure-results --single-file -o reports/allure-report --clean
