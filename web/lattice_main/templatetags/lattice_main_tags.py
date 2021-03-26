from django import template
from ..styles_map import styles_map

register = template.Library()

@register.filter
def get_len(obj):
    return len(obj)

@register.filter
def enum(obj):
    enumerated = enumerate(obj)
    return enumerated

@register.filter
def cell_patch_type(cell):
    patch_type = cell.patch_type
    return patch_type

@register.filter
def PatchType_Ancilla(patches):
    pta = patches.PatchType.Ancilla
    return pta

@register.filter
def styles_map_cell_patch_type(cell):
    """ """
    style = styles_map[cell.patch_type]
    return style

@register.filter
def styles_map_orientation(orientation):
    style = styles_map[orientation]
    return style
    
@register.filter
def styles_map_edge_color(edge_color):
    style = styles_map[edge_color]
    return style

@register.filter
def styles_map_edge_type(edge_type):
    style = styles_map[edge_type]
    return style

@register.filter
def cell_edges_items(cell):
    items = cell.edges.items()
    return items

@register.filter
def styles_map_edge_color_edge_type(edge_type):
    """styles_map['edge_color'][edge_type]"""
    style = styles_map['edge_color'][edge_type]
    return style

@register.filter
def cell_activity(cell):
    return cell.activity

@register.filter
def styles_map_activity_color_cell_activity_activity_type(cell):
    style = styles_map['activity_color'][cell.activity.activity_type]
    return style

@register.filter
def cell_text(cell):
    text = cell.text.replace("\n", "<br>")
    return text

@register.filter
def cell_font_size(cell):
    if len(cell.text) > 20: return "7"
    if len(cell.text) > 7: return "9"
    return "15"
