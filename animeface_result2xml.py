#! /usr/bin/env python

# make XML files whose format is Pascal VOC

# usage
# $ python <this script> <image dir> <xml output dir> <output filelist.txt path>

import sys
from pathlib import Path
import xml.etree.ElementTree as ET
import json
import imghdr
import copy
from pprint import pprint as print
import xml.etree.ElementTree as ET

from PIL import Image

this_file_dir = (Path(__file__).resolve()).parent

from animeface_poor_caller import detect_animeface


def image_validator(im_path, valid_img=['png', 'jpeg', 'gif']):
    file_type = imghdr.what(im_path)
    # print(file_type)
    
    if file_type in valid_img:
        return True
    else:
        return False


def mk_bbox(src_d):
    d = {}
    d['xmin'] = str(src_d['x'])
    d['ymin'] = str(src_d['y'])
    d['xmax'] = str(int(src_d['x']) + int(src_d['width']))
    d['ymax'] = str(int(src_d['y']) + int(src_d['height']))

    return d


def generate_output_file_name(file_path, xml_output_dir):
    xml_output_dir = Path(xml_output_dir)
    if not xml_output_dir.exists():
        xml_output_dir.mkdir(exist_ok=True, parents=True)

    file_path = (str(file_path)).split('/')
    file_path = file_path[1:]
    file_path = Path(xml_output_dir) / '/'.join(file_path)

    file_path = file_path.parent / (file_path.stem + '.xml')

    return str(file_path)


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
        # print(det_result)
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
    file_list = []
    for file_path in image_dir.glob('**/*'):
        if file_path.is_dir():
            continue
        if not image_validator(file_path):
            continue
        print('now detecting: ' + str(file_path))        
        file_list.append(str(file_path))    
        tree = ET.parse(str(template_path))
        element_root = tree.getroot()

        im = Image.open(str(file_path))
        w, h = im.size

        est_result = detect_animeface(file_path)
        tgt_xml = insert_det_result_to_template(est_result, element_root, (w, h))
        # import pdb; pdb.set_trace()

        output_file_name = generate_output_file_name(file_path, xml_output_dir)

        tree.write(str(output_file_name), encoding='utf-8', xml_declaration=False)

    with open(output_filelist_path, "w") as f:
        f.write('\n'.join(file_list))

if __name__ == '__main__':
    argvs = sys.argv

    assert len(argvs) == 4, "illegal argc {} != 4".format(len(argvs))

    convert_bbox2xml(argvs[1], argvs[2], argvs[3])



