# Odoo Partner Scraping

Minimal script to get partner information from https://www.odoo.com/es_ES/partners

## Use it

Just execute following line:

``` python
python partner.py
```

> Python executable be in the same forder or in PATH environment variable

## Notes

If you don't apply any changes to the code, multiple file formats will  appear
in the same folder as the script.

You can comment out lines for files you won't need.

| Line                                             | File          |
| ------------------------------------------------ | ------------- |
| ``app.save('partners.xml', file_format='xml')``  | partners.xml  |
| ``app.save('partners.xml', file_format='csv')``  | partners.csv  |
| ``app.save('partners.xml', file_format='xlsx')`` | partners.xlsx |
| ``app.save('partners.xml', file_format='json')`` | partners.json |
