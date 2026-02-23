@echo off
pytest tests/ui/ --browser=chrome --alluredir=reports/allure-results
allure generate reports/allure-results --single-file -o reports/allure-report --clean
