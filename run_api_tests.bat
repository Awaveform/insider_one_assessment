@echo off
pytest tests/api/ --alluredir=reports/allure-results
allure generate reports/allure-results --single-file -o reports/allure-report --clean
