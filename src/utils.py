import json

class dictSave:
  def __init__(self):
    pass

  def save(d: dict, filename: str):
      with open(filename, 'w') as f:
          f.write(json.dumps(d))

  def load(filename: str):
      with open(filename) as f:
          d = json.loads(f.read())
      return d


# CSS to inject contained in a string
hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """


collapsible_css = """
<style>
.collapsible {
    background-color: #777;
    color: white;
    cursor: pointer;
    padding: 18px;
    width: 100%;
    border: none;
    text-align: left;
    outline: none;
    font-size: 15px;
}

.collapsible.active, .collapsible:hover {
    background-color: #555;
}

.collapsible:after {
    content: '\002B';
    color: white;
    font-weight: bold;
    float: right;
    margin-left: 5px;
}

.collapsible.active:after {
    content: "\2212";
}

.content  {
    padding: 0 18px;
    background-color: #f1f1f1;
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.2s ease-out;
    color:black;
}
</style>
"""

collapsible_js = """
<script>
var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var content = this.nextElementSibling;
    if (content.style.display === "block") {
      content.style.display = "none";
    } else {
      content.style.display = "block";
    }
  });
}
</script>
"""