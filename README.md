# lezgi-text

## A toolkit for working with text in Lezgian language

Open source Python suite to process text data in Lezgian language.

Designed to scrap and parse periodicals in Lezgian language (newspapers, magazines, etc.).

## Installation

```
python3 -m pip install --index-url https://test.pypi.org/simple/ lezgi-text
```

or build from source

```
git clone https://github.com/Alidar40/lezgi-text.git
cd lezgi-text
pip install .
```

## Usage

### CLI app

```
lezgi_text scrap lezgi_gazet
lezgi_text parse lezgi_gazet
```

### Python library

```python
from lezgi_text import canonize_lez
canonize_lez("лезги ч1ал")
>>> 'лезги чӀал'
```