# Rosey

A Penrose tiling generator.

## Quickstart
Open `base.py`, write at the bottom of the file in the `__main__` the description of the tiling, then export it as SVG as follows:

```python
t1 = Tiling(depth=8)
t1.to_svg("output/rose.svg")
```
You can now just run the file.

```bash
python base.py
```

## References
1. [Model Implementation](https://scipython.com/blog/penrose-tiling-1/)
2. [Theoretical](https://en.wikipedia.org/wiki/Penrose_tiling)
