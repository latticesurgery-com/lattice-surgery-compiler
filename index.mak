<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Lattice Surgery QEC</title>
  <style>
  html, body{
      height: 100%;
      padding: 0;
      margin: 0;
      white-space: nowrap;
      font-size: 0;
      overflow: hidden;

  }
  #draggable-container{
  }
  .lattice-cell{
      border: 0.5px solid #a2abae;
      height: 50pt;
      width: 50pt;
      display: inline-block;
      position: relative;
      font-size:15px;
    }
  </style>
  <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
  <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
  <script>
  $( function() {
    $( "#draggable-container" ).draggable();
  } );
  </script>
</head>
<body>

<div id="draggable-container">
    %for row_idx in range(nrows):
        <div class="lattice-row">
            %for col_idx in range(ncols):
                <%
                    cell = array[row_idx][col_idx]
                %>
               <div class="lattice-cell">
                   <div class="lattice-cell-inside"
                    style="
                            height: 46pt;
                            width: 46pt;
                            vertical-align: middle;
                            display: inline-block;
                            border-width: 2pt;
                            border-style: solid;
                            border-color: transparent;
                            %if cell is not None:
                                background-color: ${styles_map[cell.patch_type]};
                                % for orientation, edge_type in cell.edges.items():
                                    border-${styles_map[orientation]}-style: ${styles_map[edge_type]};
                                    border-${styles_map[orientation]}-color: black;
                                % endfor
                            %endif
                       "
                    >
                        (${col_idx},${row_idx})
                    </div>
               </div>
            %endfor
        </div>
    %endfor
</div>


</body>
</html>