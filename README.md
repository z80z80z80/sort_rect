# sort_rect
Python library to sort rectangles (or bounding boxes) and place them in a grid, according to their position in 2D space.

## Use cases
- you have some objects with 2D coordinates and want to put them into some sort of table
- example: you know the position of each individual cell of a cell in the image of a table but not it's corresponding row/column numbers

## The catch
- this was built with tables in mind, so far it only works if there is at least one fully filled row
- so it won't work if the rectangles are for example all in one diagonal line
- a simple fix would be adding a line of dummy rectangles that defines the number of columns you're expecting

## Dependancies
- `pip install numpy`

## Example:
```python
import sort_rect

bboxes = [
        [0,0,1,1],
        [0,2,1,3],
        [2,2,3,3]
        ]

print(sort_rect.structured_cells(bboxes))
```

```
[{'col': 0, 'row': 0, 'bbox': [0, 0, 1, 1]}, {'col': 0, 'row': 1, 'bbox': [0, 2, 1, 3]}, {'col': 0, 'row': 1, 'bbox': [2, 2, 3, 3]}]
```

