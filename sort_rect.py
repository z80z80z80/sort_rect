import numpy as np

def sort_by_rows(bboxes):
    # todo: only works if bboxes are exactly in a row! I'm guessing this will only work for ground truth but not for new data
    bboxes = np.array(bboxes, dtype=object)
    bboxes = bboxes[np.lexsort((bboxes[:,0], bboxes[:,1]))] # sort by rows

    row_coord = np.unique(bboxes[:,1])
    rows = []
    
    for coord in row_coord:
        rows.append(bboxes[bboxes[:,1]==coord].tolist())
    
    return rows

def mean_col_diff(rows):      
    max_cols = []
    for i in range(len(rows)):
        row = rows[i]
        for j in range(len(row)):
            if len(np.array(row[j]).shape) > 1:  # this kind of stuff is extremely hacky, need to get array shapes under control :( 
                rows[i][j] = rows[i][j][0]
        max_cols.append(len(row))
    num_cols = np.max(max_cols)
    
    cell_x_diff = []
    for row in rows:
        if len(row) == num_cols:
            for i in range(num_cols - 1):
                cell_x_diff.append(abs(row[i+1][0]-row[i][0])) # collect the distances of each cell in x dimension, given it's a complete row
   
    return np.mean(cell_x_diff)

def resort_rows(rows, delta=1.1):
    #delta = 1.1 # todo: some kind of adjustment to the mean value I guess
    
    # calculate the mean row distance, given a rough sorting based on exact y values
    # can be used to adjust the sorting by combining rows
    
    row_height = []
    # iterate through ever row and calculate the distance to the next one
    # calculate the average row height first (should be fairly constant, might still be better to use other statistical values if variance is high)
    # based on this we can guess if seperate rows aren't seperate (ie if the distance of the top y coordinate of 2 cells is less than average row height)
    for i in range(len(rows)-1):
        row_height.append(abs(rows[i+1][0][1]-rows[i][0][1]))
    mean_row_height = np.mean(np.array(row_height).astype(int))

    new_rows = []
    if np.array(rows[0]).shape[0] > 1:
        current_row = rows[0]
    else:
        current_row = [rows[0]]
        
    for i in range(len(rows)-1):
        if abs(rows[i+1][0][1] - rows[i][0][1]) < delta * mean_row_height:
            for c in rows[i+1]:
                current_row.append(c)
        else:
            new_rows.append(current_row)          
            current_row = rows[i+1]
            
    if len(np.array(current_row).shape) < 2:
        current_row = [current_row]
        print(current_row)
    new_rows.append(current_row)
            
    return new_rows

def unique_col_coords(rows_sorted, width): # TODO: this one needs to be heavily tweaked. It's perfect value is all over the place sadly...
    
    col_x_values = []
    for row in rows_sorted:
        for cell in row:            
            if len(np.array(cell).shape) >1:      
                print(cell)
                col_x_values.append(cell[0][0])
            else:
                col_x_values.append(cell[0])
        
    tolerance = mean_col_diff(rows_sorted)
    delta = width/tolerance*100

    # compares every of the possible column x values with each other given a maximum difference (tolerance)
    # returns a list of of columns with it's possible x values
    options = np.unique(col_x_values)

    unique = []
    for o0 in options:
        kinda_unique = []
        for o1 in options:
            if (abs(o0-o1) < tolerance - delta):
                kinda_unique.append(o1)
        unique.append(kinda_unique)

    unique = np.unique(unique)
    
    for i in range(len(unique)-1):
        col = unique[i]
        for coord in col:
            for j in range(len(unique)-i-1):
                sub = unique[j+i+1]
                for k in range(len(sub)):
                    if coord == sub[k]:
                        #print(coord, sub)
                        sub.pop(k)
                        break

    return unique

def get_col(unique_cols, cell):
    for i in range(len(unique_cols)):
        try: 
            iter(unique_cols[i])
        except:
            unique_cols = unique_cols.tolist()
            unique_cols[i] = [unique_cols[i]]
            unique_cols = np.array(unique_cols, dtype=object)
            
        for coord in unique_cols[i]:
            if coord == cell[0]:
                return i
    
    return None

def structured_cells(bboxes, delta=1.1, width=300):
    try:
        done = False
        steps = int(delta/0.005)
                
        for j in range(steps):
            rough_sorted = sort_by_rows(bboxes)
            sorted_rows = resort_rows(rough_sorted, delta)
            unique_cols = unique_col_coords(sorted_rows, width)

            cells = []
            for i in range(len(sorted_rows)):
                row = sorted_rows[i]        
                for cell in row:
                    cell_dict = {}
                    col_num = get_col(unique_cols, cell)
                    if col_num == None:
                        col_num = 0
                    cell_dict['col'] = col_num
                    cell_dict['row'] = i
                    cell_dict['bbox'] = cell
                    cells.append(cell_dict)            
            if len(cells) == len(bboxes):
                return cells, len(sorted_rows), len(unique_cols)
            else:
                delta = delta - delta2
                
    except:
        raise Exception('Might be something unrelated BUT: You need to supply a list with at least 2 bounding boxes in the style [x0,y0,x1,y1]')
