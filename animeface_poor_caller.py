# a poor python caller of animeface-2009
# call rb module via shell by using subprocess...

import subprocess

import sys
import json
from PIL import Image
from pathlib import Path

this_file_dir = (Path(__file__).resolve()).parent

import re


def _draw_det_image(im, result_list, output_path):
    draw = ImageDraw.Draw(im)
    for res in result_list:
        draw.rectangle((res['face']['x'], res['face']['y'], res['face']['x'] + res['face']['width'], res['face']['y'] + res['face']['height']), outline=(0, 255, 0))
        draw.rectangle((res["eyes"]["right"]['x'], res["eyes"]["right"]['y'], res["eyes"]["right"]['x'] + res["eyes"]["right"]['width'], res["eyes"]["right"]['y'] + res["eyes"]["right"]['height']), outline=(0, 255, 0))
        draw.rectangle((res["eyes"]["left"]['x'], res["eyes"]["left"]['y'], res["eyes"]["left"]['x'] + res["eyes"]["left"]['width'], res["eyes"]["left"]['y'] + res["eyes"]["left"]['height']), outline=(0, 255, 0))
        draw.rectangle((res["mouth"]['x'], res["mouth"]['y'], res["mouth"]['x'] + res["mouth"]['width'], res["mouth"]['y'] + res["mouth"]['height']), outline=(0, 255, 0))
        draw.rectangle((res["nose"]['x'], res["nose"]['y'], res["nose"]['x'] + 1, res["nose"]['y'] + 1), outline=(0, 255, 0))
        draw.rectangle((res["chin"]['x'], res["chin"]['y'], res["chin"]['x'] + 1, res["chin"]['y'] + 1), outline=(0, 255, 0))

    im.save(output_path)


def detect_animeface(im_path):

    im_path = Path(im_path).resolve()
    assert im_path.exists()

    ruby_script_path = this_file_dir / 'animeface-2009/animeface-ruby/sample.rb'
    ret = subprocess.check_output(["ruby", str(ruby_script_path), str(im_path)]).decode('utf-8')

    ret = ret.replace("=>", ":")
    ret = ret.replace(">", "\"")
    ret = ret.replace("#", "\"")
    # delete original 2 lines
    #ret = ret.replace("\n1 faces\nSee sample_out.png\n", '')
    #ret = re.sub(r"\n.+ faces\nSee .+\n", '', ret)
    # print(im_path, ret)
    list_ = json.loads(ret)

    return list_


if __name__ == '__main__':

    from PIL import Image, ImageDraw

    argvs = sys.argv
    im_path = Path(argvs[1])

    assert im_path.exists(), im_path
    
    result_list = detect_animeface(im_path)

    im = Image.open(str(im_path))
    # output_path = im_path.parent / (im_path.stem + '_out.png')
    output_path = im_path.stem + '_out.png'
    _draw_det_image(im, result_list, output_path)


    print(result_list)
