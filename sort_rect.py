import numpy as np

def sort_by_rows(bboxes):
    # todo: only works if bboxes are exactly in a row! I'm guessing this will only work for ground truth but not for new data
    bboxes = np.array(bboxes)
    bboxes = bboxes[np.lexsort((bboxes[:,0], bboxes[:,1]))] # sort by rows

    row_coord = np.unique(bboxes[:,1])
    rows = []
    
    for coord in row_coord:
        rows.append(bboxes[bboxes[:,1]==coord].tolist())
    
    return rows

def mean_col_diff(rows):      
    max_cols = []
    for row in rows:
        max_cols.append(len(row))
    num_cols = np.max(max_cols)

    cell_x_diff = []
    for row in rows:
        if len(row) == num_cols:
            for i in range(num_cols - 1):
                cell_x_diff.append(abs(row[i+1][0]-row[i][0])) # collect the distances of each cell in x dimension, given it's a complete row
   
    return np.mean(cell_x_diff)

def resort_rows(rows):
    delta = 1.1 # todo: some kind of adjustment to the mean value I guess
    
    # calculate the mean row distance, given a rough sorting based on exact y values
    # can be used to adjust the sorting by combining rows
    
    row_height = []
    # iterate through ever row and calculate the distance to the next one
    # calculate the average row height first (should be fairly constant, might still be better to use other statistical values if variance is high)
    # based on this we can guess if seperate rows aren't seperate (ie if the distance of the top y coordinate of 2 cells is less than average row height)
    for r in rows:
        row_height.append(abs(r[0][1]-r[0][3]))
    mean_row_height = np.mean(row_height)
    
    new_rows = []
    current_row = [rows[0]]
    for i in range(len(rows)-1):
        if abs(rows[i+1][0][1] - rows[i][0][1]) < delta * mean_row_height:
            current_row.append(row[i+1])
        else:
            new_rows.append(current_row)
            current_row = [rows[i+1]]
            
    if abs(rows[i+1][0][1] - rows[i][0][1]) >= delta * mean_row_height: # to catch the last row
        new_rows.append(current_row)
        
        
    cleaned = []
    for row in new_rows:
        for sub in row:
            cleaned.append(sub)

    return cleaned

def unique_col_coords(rows_sorted):
    
    col_x_values = []
    for row in rows_sorted:
        for cell in row:
            col_x_values.append(cell[0])
        
    delta = .5 # todo: needs adjustment or something else than just the mean in mean_col_diff
    tolerance = mean_col_diff(rows_sorted) * delta

    # compares every of the possible column x values with each other given a maximum difference (tolerance)
    # returns a list of of columns with it's possible x values
    options = np.unique(col_x_values)

    unique = []
    for o0 in options:
        kinda_unique = []
        for o1 in options:
            if abs(o0-o1) < tolerance:
                kinda_unique.append(o1)
        unique.append(kinda_unique)

    return np.unique(unique)

def get_col(unique_cols, cell):
    for i in range(len(unique_cols)):
        try: 
            iter(unique_cols[i])
        except:
            unique_cols = unique_cols.tolist()
            unique_cols[i] = [unique_cols[i]]
            unique_cols = np.array(unique_cols)
            
        for coord in unique_cols[i]:
            if coord == cell[0]:
                return i
    
    return None

def structured_cells(bboxes):
    try:
        rough_sorted = sort_by_rows(bboxes)
        sorted_rows = resort_rows(rough_sorted)
        unique_cols = unique_col_coords(sorted_rows)
        
        cells = []
        for i in range(len(sorted_rows)):
            row = sorted_rows[i]        
            for cell in row:
                cell_dict = {}
                col_num = get_col(unique_cols, cell)
                if col_num == None:
                    print("ERROR!!!")
                cell_dict['col'] = col_num
                cell_dict['row'] = i
                cell_dict['bbox'] = cell
                cells.append(cell_dict)            
    
        return cells

    except:
        raise Exception('Might be something unrelated BUT: You need to supply a list with at least 2 bounding boxes in the style [x0,y0,x1,y1]')
