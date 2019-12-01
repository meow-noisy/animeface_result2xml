#! /usr/bin/env python

# make XML files whose format is Pascal VOC

# usage
# $ python <this script> <image dir> <xml output dir> <output filelist.txt path>

import sys
from pathlib import Path
import xml.etree.ElementTree as ET
import json
import xmljson
import imghdr
import copy
from pprint import pprint as print
import dicttoxml
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET


from PIL import Image

this_file_dir = (Path(__file__).resolve()).parent

from animeface_poor_wrapper import detect_animeface


def load_xml_template(template_path):

    assert template_path.exists(), template_path
    tree = ET.parse(template_path)
    root = tree.getroot()

    voc_template_dic = json.dumps(xmljson.yahoo.data(root))
    voc_template_dic = json.loads(voc_template_dic)

    return voc_template_dic


def image_validator(im_path, valid_img=['png', 'jpeg', 'gif']):
    file_type = imghdr.what(im_path)
    # print(file_type)
    
    if file_type in valid_img:
        return True
    else:
        return False


def _insert_bbox(src_d, tgt_d):
    tgt_d['xmin'] = src_d['x']
    tgt_d['ymin'] = src_d['y']
    tgt_d['xmax'] = str(int(src_d['x']) + int(src_d['width']))
    tgt_d['ymax'] = str(int(src_d['y']) + int(src_d['height']))


def mk_bbox(src_d):
    d = {}
    d['xmin'] = str(src_d['x'])
    d['ymin'] = str(src_d['y'])
    d['xmax'] = str(int(src_d['x']) + int(src_d['width']))
    d['ymax'] = str(int(src_d['y']) + int(src_d['height']))

    return d


def _insert_det_result_to_template(det_result_list, template, im_size):

    output_dic_list = []

    (w, h) = im_size

    # 小さい物体の辺のサイズ
    small_obj_edge = max((min(w, h) / 20), 10)

    tgt_dic = copy.deepcopy(template)
    tgt_dic['annotation']['size']['height'] = h
    tgt_dic['annotation']['size']['width'] = w

    for det_result in det_result_list:
        
        obj_dic = copy.deepcopy(tgt_dic['annotation']["object"])

        for tgt_part_dic in obj_dic:
            face_parts_name = tgt_part_dic["name"]

            if face_parts_name == "face":
                _insert_bbox(det_result["face"], tgt_part_dic["bndbox"])
            elif face_parts_name == "right_eye":
                _insert_bbox(det_result["eyes"]["right"], tgt_part_dic["bndbox"])
            elif face_parts_name == "left_eye":
                _insert_bbox(det_result["eyes"]["left"], tgt_part_dic["bndbox"])
            elif face_parts_name == "nose":
                det_result["nose"]["width"] = small_obj_edge
                det_result["nose"]["height"] = small_obj_edge
                _insert_bbox(det_result["nose"], tgt_part_dic["bndbox"])
            elif face_parts_name == "mouth":
                _insert_bbox(det_result["mouth"], tgt_part_dic["bndbox"])
            elif face_parts_name == "chin":
                det_result["chin"]["width"] = small_obj_edge
                det_result["chin"]["height"] = small_obj_edge
                _insert_bbox(det_result["chin"], tgt_part_dic["bndbox"])
            else:
                raise Error()

    
        output_dic_list.append(obj_dic)

    tgt_dic['annotation']["object"] = output_dic_list

    return tgt_dic


def generate_output_file_name(file_path, xml_output_dir):
    
    file_path = (str(file_path)).split('/')
    file_path = file_path[1:]
    file_path = Path(xml_output_dir) / '/'.join(file_path)

    file_path = file_path.parent / (file_path.stem + '.xml')

    return str(file_path)


def output_xml(updated_result_dict):
    # XMLをアウトプットする
    
    #import pdb; pdb.set_trace()
    xml = dicttoxml.dicttoxml(updated_result_dict, root=False, attr_type=False)

    from xml.dom.minidom import parseString
    dom = parseString(xml)
    output_result = dom.toprettyxml()

    return output_result
    

def dirty_postedit1(dic_):
    if dic_['annotation']['object'] == []:
        return
    if len(dic_['annotation']['object']) == 1:
        dic_['annotation']['object'] = dic_['annotation']['object'][0]


def dirty_postedit2(output_result):

    output_result = output_result.replace('<?xml version="1.0" ?>\n', '')
    output_result = output_result.replace('<object>\n\t', '')
    output_result = output_result.replace('</object>\n', '')
    output_result = output_result.replace('<item>', '<object>')
    output_result = output_result.replace('</item>', '</object>')

    return output_result


def _add_elem(name, bbox_dic, et):
    o = ET.SubElement(et,  "object")
    e = ET.SubElement(o,  "name")
    e.text = name

    e = ET.SubElement(o,  "pose")
    e.text = 'Unspecified'

    e = ET.SubElement(o,  "truncated")
    e.text = '1'

    e = ET.SubElement(o,  "difficult")
    e.text = '0'

    e = ET.SubElement(o,  "bndbox")
    b = ET.SubElement(e,  "xmin")
    b.text = bbox_dic['xmin']

    b = ET.SubElement(e,  "ymin")
    b.text = bbox_dic['ymin']

    b = ET.SubElement(e,  "xmax")
    b.text = bbox_dic['xmax']

    b = ET.SubElement(e,  "ymax")
    b.text = bbox_dic['ymax']


def insert_det_result_to_template(det_result_list, tgt_xml, im_size):

    output_dic_list = []

    (w, h) = im_size

    # 小さい物体の辺のサイズ
    small_obj_edge = max((min(w, h) / 20), 10)

    tgt_xml[4][0].text = str(w)
    tgt_xml[4][1].text = str(h)

    for det_result in det_result_list:
        print(det_result)
        d = mk_bbox(det_result["face"])
        _add_elem("face", d, tgt_xml)
        
        d = mk_bbox(det_result["eyes"]["right"])
        _add_elem("right_eye", d, tgt_xml)
        
        d = mk_bbox(det_result["eyes"]["left"])
        _add_elem("left_eye", d, tgt_xml)
        
        det_result["nose"]["width"] = small_obj_edge
        det_result["nose"]["height"] = small_obj_edge
        d = mk_bbox(det_result["nose"])
        _add_elem("nose", d, tgt_xml)
        
        d = mk_bbox(det_result["mouth"])
        _add_elem("mouth", d, tgt_xml)
        
        det_result["chin"]["width"] = small_obj_edge
        det_result["chin"]["height"] = small_obj_edge
        d = mk_bbox(det_result["chin"])
        _add_elem("chin", d, tgt_xml)


    return tgt_xml


def convert_bbox2xml(image_dir, xml_output_dir, output_filelist_path):
    
    # load xml template
    template_path = this_file_dir / 'data/template.xml'

    image_dir = Path(image_dir)
    assert image_dir.exists(), image_dir

    # import pdb; pdb.set_trace()

    for file_path in image_dir.glob('**/*'):
        print(file_path)
        if file_path.is_dir():
            continue
        if not image_validator(file_path):
            continue

        tree = ET.parse(str(template_path))
        element_root = tree.getroot()

        im = Image.open(str(file_path))
        w, h = im.size

        est_result = detect_animeface(file_path)
        tgt_xml = insert_det_result_to_template(est_result, element_root, (w, h))
        # import pdb; pdb.set_trace()

        output_file_name = generate_output_file_name(file_path, xml_output_dir)

        tree.write(str(output_file_name), encoding='utf-8', xml_declaration=False)



def _convert_bbox2xml(image_dir, xml_output_dir, output_filelist_path):
    
    # load xml template
    template_path = this_file_dir / 'data/template.xml'
    template_dic = load_xml_template(template_path)

    image_dir = Path(image_dir)
    assert image_dir.exists(), image_dir

    # import pdb; pdb.set_trace()

    for file_path in image_dir.glob('**/*'):
        print(file_path)
        if file_path.is_dir():
            continue
        if not image_validator(file_path):
            continue

        im = Image.open(str(file_path))
        w, h = im.size

        est_result = detect_animeface(file_path)
        #import pdb; pdb.set_trace()
        updated_result = insert_det_result_to_template(est_result, template_dic, (w, h))
        dirty_postedit1(updated_result)

        output_file_name = generate_output_file_name(file_path, xml_output_dir)

        output_result = output_xml(updated_result)

        output_result = dirty_postedit2(output_result)

        output_file_name  = Path(output_file_name)
        with output_file_name.open('w') as f:
            f.write(output_result)

        print(updated_result)


if __name__ == '__main__':
    argvs = sys.argv

    assert len(argvs) == 4, "illegal argc {} != 4".format(len(argvs))

    convert_bbox2xml(argvs[1], argvs[2], argvs[3])



