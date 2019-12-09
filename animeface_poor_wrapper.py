# a poor python wrapper of animeface-2009
# call rb module via shell by using subprocess...

import subprocess

import sys
import json

from pathlib import Path

this_file_dir = (Path(__file__).resolve()).parent

import re


def detect_animeface(im_path):

    im_path = Path(im_path).resolve()
    assert im_path.exists()

    ruby_script_path = this_file_dir / 'animeface2009/animeface-ruby/sample.rb'
    ret = subprocess.check_output(["ruby", str(ruby_script_path), str(im_path)]).decode('utf-8')

    ret = ret.replace("=>", ":")
    ret = ret.replace(">", "\"")
    ret = ret.replace("#", "\"")
    # delete original 2 lines
    #ret = ret.replace("\n1 faces\nSee sample_out.png\n", '')
    ret = re.sub(r"\n.+ faces\nSee .+\n", '', ret)
    # print(im_path, ret)
    dic = json.loads(ret)

    return dic


if __name__ == '__main__':
    argvs = sys.argv
    im_path = argvs[1]

    d = detect_animeface(im_path)

    print(d)
