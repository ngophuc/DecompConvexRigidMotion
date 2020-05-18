""""
Demonstration of paper:  Rigid motion using convex decomposition
demo editor: Phuc Ngo
"""

from lib import base_app, build, http, image, config
from lib.misc import app_expose, ctime
from lib.base_app import init_app

import cherrypy
from cherrypy import TimeoutError
import os.path
import shutil
import time


class app(base_app):
    """ template demo app """

    title = "Rigid Motion Using Convex Decomposition: Online Demonstration"
    xlink_article = 'http://www.ipol.im/'
    #xlink_src = 'http://www.ipol.im/pub/pre/67/gjknd_1.1.tgz'
    #dgtal_src = 'https://github.com/kerautret/DGtal.git'
    #demo_src_filename  = 'gjknd_1.1.tgz'
    demo_src_dir = 'DecompConvexRigidMotion'

    input_nb = 1 # number of input images
    input_max_pixels = 4096 * 4096 # max size (in pixels) of an input image
    input_max_weight = 1 * 4096 * 4096  # max size (in bytes) of an input file
    input_dtype = '3x8i' # input image expected data type
    input_ext = '.png'   # input image expected extension (ie file format)
    is_test = False      # switch to False for deployment
    commands = []
    def __init__(self):
        """
        app setup
        """
        # setup the parent class
        base_dir = os.path.dirname(os.path.abspath(__file__))
        base_app.__init__(self, base_dir)

        # select the base_app steps to expose
        # index() is generic
        app_expose(base_app.index)
        app_expose(base_app.input_select)
        app_expose(base_app.input_upload)
        # params() is modified from the template
        app_expose(base_app.params)
        # run() and result() must be defined here




    def build(self):
        """
        program build/update
        """
        """
        # store common file path in variables
        tgz_file = self.dl_dir + self.demo_src_filename
        prog_names = ["pgm2freeman", "displayContours", "extract3D"]
        script_names = ["convert.sh", "convertFig.sh", "transformBG.sh"]
        prog_bin_files = []

        for a_prog in prog_names:
            prog_bin_files.append(self.bin_dir+ a_prog)

        log_file = self.base_dir + "build.log"
        # get the latest source archive

        build.download(self.xlink_src, tgz_file)

        # test if the dest file is missing, or too old
        if (os.path.isfile(prog_bin_files[0])
            and ctime(tgz_file) < ctime(prog_bin_files[0])):
            cherrypy.log("not rebuild needed",
                         context='BUILD', traceback=False)
        else:
            # extract the archive
            build.extract(tgz_file, self.src_dir)
            # build the program
            os.mkdir(self.src_dir+ self.demo_src_dir+ "/build")
            build.run("cd %s; cmake .. -DBUILD_EXAMPLES=false \
                       -DCMAKE_BUILD_TYPE=Release \
                       -DDGTAL_BUILD_TESTING=false;\
                       make -j 4"%(self.src_dir+ self.demo_src_dir + "/build")\
                      , stdout=log_file)

            # save into bin dir
            if os.path.isdir(self.bin_dir):
                shutil.rmtree(self.bin_dir)
            os.mkdir(self.bin_dir)
            for i in range(0, len(prog_bin_files)):
                shutil.copy(self.src_dir +
                            os.path.join(self.demo_src_dir,
                                         "build",
                                         "demoIPOL_ExtrConnectedReg",
                                         prog_names[i]),
                            prog_bin_files[i])
            for s_name in script_names:
                shutil.copy(self.src_dir+
                            os.path.join(self.demo_src_dir,
                                         "demoIPOL_ExtrConnectedReg",
                                         s_name), self.bin_dir)
            # copy Dynamic lib
            shutil.copy(self.src_dir +self.demo_src_dir+
                        "/build/src/libDGtal.so", self.bin_dir)
            shutil.copy(self.src_dir +self.demo_src_dir+
                        "/build/src/libDGtalIO.so", self.bin_dir)
            # cleanup the source dir
            shutil.rmtree(self.src_dir)
        """    
        return

       
    def input_select_callback(self, fnames):
        '''
        Implement the callback for the input select to
        process the non-standard input
        '''         
        extension3D = (fnames[0])[-6:-4]
        if( extension3D == "3d" ):
            self.cfg['meta']['is3d'] = True
        else:
            self.cfg['meta']['is3d'] = False
        
        if self.cfg['meta']['is3d'] :
            baseName = (fnames[0])[0:-4]
            shutil.copy(self.input_dir + baseName+".obj",
                        self.work_dir + 'inputVol_0.obj')        
        self.cfg.save()
    
    #---------------------------------------------------------------------------
    # Parameter handling (an optional crop).
    #---------------------------------------------------------------------------
    @cherrypy.expose
    @init_app
    def wait(self, **kwargs):
        """
        params handling and run redirection
        """
        if not 'is3d' in  self.cfg['meta']:
            self.cfg['meta']['is3d'] = False
        try:
            self.cfg['param']['tx'] = 0
            self.cfg['param']['ty'] = 0
            self.cfg['param']['tz'] = 0
            self.cfg['param']['theta'] = 0
            self.cfg['param']['alpha'] = 0
            self.cfg['param']['beta'] = 0
            self.cfg['param']['gamma'] = 0
            self.cfg['param']['sampling'] = 1
            self.cfg['param']['resolution'] = 100000
            self.cfg['param']['depth'] = 20
            self.cfg['param']['minvolumeperch'] = 0.0001
            self.cfg['param']['regu'] =  True
            if(self.cfg['meta']['is3d']):
                self.cfg['param']['tx'] = kwargs['tx']
                self.cfg['param']['ty'] = kwargs['ty']
                self.cfg['param']['tz'] = kwargs['tz']
                self.cfg['param']['alpha'] = kwargs['alpha']  
                self.cfg['param']['beta'] = kwargs['beta']  
                self.cfg['param']['gamma'] = kwargs['gamma']  
                self.cfg['param']['sampling'] = kwargs['sampling']
                self.cfg['param']['resolution'] = kwargs['resolution']
                self.cfg['param']['depth'] = kwargs['depth']
                self.cfg['param']['minvolumeperch'] = kwargs['minvolumeperch']
            else : 
                self.cfg['param']['regu'] =  kwargs['regu'] == 'True'
                self.cfg['param']['tx'] = kwargs['tx']
                self.cfg['param']['ty'] = kwargs['ty']
                self.cfg['param']['theta'] = kwargs['theta']    
            self.cfg.save()

        except ValueError:
            return self.error(errcode='badparams',
                              errmsg="The parameters must be numeric.")

        http.refresh(self.base_url + 'run?key=%s' % self.key)
        return self.tmpl_out("wait.html")

    @cherrypy.expose
    @init_app
    def run(self):
        """
        algo execution
        """
        # read the parameters
        self.commands = ""
        # run the algorithm
        try:
            self.run_algo(self)
        except TimeoutError:
            return self.error(errcode='timeout',
                              errmsg="Try again with simpler images.")
        except RuntimeError:
            return self.error(errcode='runtime',
                              errmsg="Something went wrong with the program.")
        except ValueError:
            return self.error(errcode='badparams',
                              errmsg="The parameters given produce no contours,\
                              please change them.")

        http.redir_303(self.base_url + 'result?key=%s' % self.key)

        # archive
        if self.cfg['meta']['original']:
            ar = self.make_archive()
            ar.add_file("input_0.png", "original.png", info="uploaded")
            ar.add_file("algoLog.txt", info="algoLog.txt")
            ar.add_file("commands.txt", info="commands.txt")
            ar.add_file("input_0.pgm", info="input_0.pgm")
            ar.add_file("result_0.png", "result_0.png", info="result_0.png")
            ar.add_file("result_poly.png", "result_poly.png", info="result_poly.png")
            ar.add_file("result_decomp.png", "result_decomp.png", info="result_decomp.png")
            ar.add_file("result_shape.png", "result_shape.png", info="result_shape.png")
            
            ar.save()
        return self.tmpl_out("run.html")

    def run_algo(self, params):
        """
        the core algo runner
        could also be called by a batch processor
        this one needs no parameter
        """
        #----------
        # 2D case
        #----------
        if  not self.cfg['meta']['is3d']:
            ##  -------
            ## process 1: transform input file
            ## ---------
            command_args = ['convert.sh', 'input_0.png', 'input_0.pgm' ]
            self.runCommand(command_args)

            ##  -------
            ## process 2: apply algorithm
            ## ---------
            inputWidth = image(self.work_dir + 'input_0.png').size[0]
            inputHeight = image(self.work_dir + 'input_0.png').size[1]
            if not self.cfg['param']['regu']:
                command_args = ['transformDecomShape2d'] + \
                           [ '-i', 'input_0.pgm', '-o', 'result_0.pgm'] + \
                           ['-d', self.base_dir+os.path.join('bin/')] + \
                           ['-e'] + \
                           ['-a', str(self.cfg['param']['tx'])] + \
                           ['-b', str(self.cfg['param']['ty'])] + \
                           ['-t', str(self.cfg['param']['theta'])]
            else:
                command_args = ['transformDecomShape2d'] + \
                           [ '-i', 'input_0.pgm', '-o', 'result_0.pgm'] + \
                           ['-d', self.base_dir+os.path.join('bin/')] + \
                           ['-e', '-r'] + \
                           ['-a', str(self.cfg['param']['tx'])] + \
                           ['-b', str(self.cfg['param']['ty'])] + \
                           ['-t', str(self.cfg['param']['theta'])]               
            fInfo = open(self.work_dir+"algoLog.txt", "w")
            cmd = self.runCommand(command_args, None, fInfo)
            fInfo.close()
            
            ## ---------
            ## process 3: convert output results
            ## ---------
            widthDisplay = max(inputWidth, 512)
            fInfo = open(self.work_dir+"algoLog.txt", "a")
            command_args = ['convert.sh', '-flatten', \
                            'result_0.pgm', '-negate', '-geometry', str(widthDisplay)+"x", 'result_0.png']
            self.runCommand(command_args, None, fInfo)
            fInfo.close()

            ##----------
            fInfo = open(self.work_dir+"algoLog.txt", "a")
            command_args = ['convert.sh', '-flatten', \
                            'input_0_poly.eps', '-geometry', str(widthDisplay)+"x", 'result_poly.png']
            self.runCommand(command_args, None, fInfo)
            fInfo.close()

            ##----------
            fInfo = open(self.work_dir+"algoLog.txt", "a")
            command_args = ['convert.sh', '-flatten', \
                            'input_0_decomp.eps', '-geometry', str(widthDisplay)+"x", 'result_decomp.png']
            self.runCommand(command_args, None, fInfo)
            fInfo.close()

            ##----------
            fInfo = open(self.work_dir+"algoLog.txt", "a")
            command_args = ['convert.sh', '-flatten', \
                            'input_0_shape.eps', '-geometry', str(widthDisplay)+"x", 'result_shape.png']
            self.runCommand(command_args, None, fInfo)
            fInfo.close()

        #----------
        # 3D case
        #----------
        else:
            ##  -------
            ## apply algorithm
            ## ---------
            command_args = ['transformDecomShape3d'] + \
                           ['-i', 'inputVol_0.obj', '-o', 'outputVol_0.obj'] + \
                           ['-d', self.base_dir+os.path.join('bin/')] + \
                           ['-x', str(self.cfg['param']['tx'])] + \
                           ['-y', str(self.cfg['param']['ty'])] + \
                           ['-z', str(self.cfg['param']['tz'])] + \
                           ['-a', str(self.cfg['param']['alpha'])] + \
                           ['-b', str(self.cfg['param']['beta'])] + \
                           ['-g', str(self.cfg['param']['gamma'])] + \
                           ['-s', str(self.cfg['param']['sampling'])] + \
                           ['-r', str(self.cfg['param']['resolution'])] + \
                           ['--depth', str(self.cfg['param']['depth'])] + \
                           ['-m', str(self.cfg['param']['minvolumeperch'])]
            #Convert sdp to objet for the results here !
            fInfo = open(self.work_dir+"algoLog.txt", "w")
            cmd = self.runCommand(command_args, None, fInfo)
            fInfo.close()

        fcommands = open(self.work_dir+"commands.txt", "w")
        fcommands.write(self.commands)
        fcommands.close()
        return


    @cherrypy.expose
    @init_app
    def result(self, public=None):
        """
        display the algo results
        """
        resultHeight = image(self.work_dir + 'input_0.png').size[1]
        imageHeightResized = min (600, resultHeight)
        resultHeight = max(200, resultHeight)
        return self.tmpl_out("result.html", height=resultHeight, \
                             heightImageDisplay=imageHeightResized, \
                             width=image(self.work_dir\
                                           +'input_0.png').size[0])


    def runCommand(self, command, stdOut=None, stdErr=None, comp=None,
                   outFileName=None):
        """
        Run command and update the attribute list_commands
        """
        p = self.run_proc(command, stderr=stdErr, stdout=stdOut, \
                          env={'LD_LIBRARY_PATH' : self.bin_dir})
        self.wait_proc(p, timeout=self.timeout)
        index = 0
        # transform convert.sh in it classic prog command (equivalent)
        for arg in command:
            if arg == "convert.sh" :
                command[index] = "convert"
            index = index + 1
        command_to_save = ' '.join(['"' + arg + '"' if ' ' in arg else arg
                 for arg in command ])
        if comp is not None:
            command_to_save += comp
        if outFileName is not None:
            command_to_save += ' > ' + outFileName

        self.commands +=  command_to_save + '\n'
        return command_to_save
