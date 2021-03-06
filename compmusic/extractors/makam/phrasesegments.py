# Copyright 2013,2014 Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of Dunya
#
# Dunya is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation (FSF), either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/
import os
import shutil
import compmusic.extractors
import subprocess
import socket

import tempfile
import wave
import subprocess
from compmusic import dunya
dunya.set_token('69ed3d824c4c41f59f0bc853f696a7dd80707779')

class PhraseSeg(compmusic.extractors.ExtractorModule):
    _version = "0.1"
    _sourcetype = "txt"
    _slug = "phraseseg"
    _many_files = True

    _output = {
         "segments": {"extension": "dat", "mimetype": "text/plain",  "parts": True},
         "mapping": {"extension": "json", "mimetype": "application/json" }
         }

    def run_many(self, id_fnames):
        server_name = socket.gethostname()
        subprocess_env = os.environ.copy()
        subprocess_env["MCR_CACHE_ROOT"] = "/tmp/emptydir"
        subprocess_env["LD_LIBRARY_PATH"] = "/mnt/compmusic/%s/MATLAB/MATLAB_Compiler_Runtime/v85/runtime/glnxa64:/mnt/compmusic/%s/MATLAB/MATLAB_Compiler_Runtime/v85/bin/glnxa64:/mnt/compmusic/%s/MATLAB/MATLAB_Compiler_Runtime/v85/sys/os/glnxa64" % ((server_name,)*3)
        #subprocess_env["LD_LIBRARY_PATH"] = "/usr/local/MATLAB/MATLAB_Runtime/v85/runtime/glnxa64:/usr/local/MATLAB/MATLAB_Runtime/v85/bin/glnxa64:/usr/local/MATLAB/MATLAB_Runtime/v85/sys/os/glnxa64/:/usr/local/MATLAB/MATLAB_Runtime/v85/sys/java/jre/glnxa64/jre/lib/amd64/:/usr/local/MATLAB/MATLAB_Runtime/v85/sys/java/jre/glnxa64/jre/lib/amd64/server"
        
        tmp_folder = tempfile.mkdtemp()
        for mbid, f_path  in id_fnames:
            dst = os.path.join(tmp_folder, os.path.basename(f_path))
            shutil.copy(f_path, dst)
        
        proc = subprocess.Popen(["/srv/dunya/phraseSeg segment %s %s" % (tmp_folder, '/srv/dunya/results.mat')], stdout=subprocess.PIPE, shell=True, env=subprocess_env)
        
        (out, err) = proc.communicate()
        
        ret = {'segments': [], 'mapping': {}}
        count = 1
        for f in os.listdir(tmp_folder):
            if f.endswith(".seg"):
                json_file = open(os.path.join(tmp_folder, f))
                ret["segments"].append(json_file.read())
                ret['mapping'][count] = os.path.basename(f).replae('.seg','')
                json_file.close()
                count += 1
            os.remove(os.path.join(tmp_folder, f))
        os.rmdir(tmp_folder)
        
        return ret 
