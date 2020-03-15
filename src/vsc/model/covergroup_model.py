
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.


from vsc.model.coverpoint_model import CoverpointModel
from vsc.model.coverpoint_cross_model import CoverpointCrossModel
from vsc.model.composite_field_model import CompositeFieldModel

'''
Created on Aug 3, 2019

@author: ballance
'''

class CovergroupModel(CompositeFieldModel):
    
    def __init__(self, name:str):
        super().__init__(name)
        
        # Handle to the type covergroup this instance is associated with
        self.type_cg : CovergroupModel = None
        
        # List of covergroup instances of this type
        self.cg_inst_l : List[CovergroupModel] = []
        
        self.coverpoint_l = []
        self.cross_l = []
        self.typename = None # Typename of this covergroup
        self.du_name = None # Design-unit typename in which this covergroup is instanced
        self.instname = None # Design-unit instance name in which this covergroup is instanced
        
        
    def finalize(self):
        for cp in self.coverpoint_l:
            cp.finalize()
            
        for cp in self.cross_l:
            cp.finalize()

    def sample(self):
        # First, sample the coverpoints
        for cp in self.coverpoint_l:
            cp.sample()
            
        for cr in self.cross_l:
            cr.sample()

        if self.type_cg is not None:
            # Propagate cached values to the type
            for i in range(len(self.coverpoint_l)):
                self.type_cg.coverpoint_l[i].target_val_cache = self.coverpoint_l[i].target_val_cache

            # Now, sample the type
            self.type_cg.sample()
            
    def add_coverpoint(self, cp):
        cp.parent = self
        if isinstance(cp, CoverpointModel):
            self.coverpoint_l.append(cp)
        elif isinstance(cp, CoverpointCrossModel):
            self.cross_l.append(cp)
        else:
            raise Exception("Unsupported model type %s" % (str(type(cp))))
        
        return cp
        
    def get_coverage(self):
        ret = 0.0
        for cp in self.coverpoint_l:
            ret += cp.get_coverage()
        for cp in self.cross_l:
            ret += cp.get_coverage()
        if (len(self.coverpoint_l)+len(self.cross_l)) == 0:
            return 100.0 # vacuously covered
        else:
            return (ret / (len(self.coverpoint_l) + len(self.cross_l)))
    
    def get_inst_coverage(self):
        return 0.0
            
    def accept(self, v):
        v.visit_covergroup(self)
            
    def dump(self, ind=""):
        print(ind + "Covergroup " + self.name)
        for cp in self.coverpoint_l:
            cp.dump(ind + "    ")
        for cr in self.cross_l:
            cr.dump(ind + "    ")

    def equals(self, oth : 'CovergroupModel')->bool:
        eq = True
        
        eq &= (self.name == oth.name)

        if len(self.coverpoint_l) == len(oth.coverpoint_l):
            for i in range(len(self.coverpoint_l)):
                eq &= self.coverpoint_l[i].equals(oth.coverpoint_l[i])
        else:
            eq = False                
            
        if len(self.cross_l) == len(oth.cross_l):
            for i in range(len(self.cross_l)):
                eq &= self.cross_l[i].equals(oth.cross_l[i])
        else:
            eq = False
            
        return eq
    
    def clone(self)->'CovergroupModel':
        ret = CovergroupModel(self.name)
        
        ret.du_name = self.du_name
        ret.instname = self.instname
        
        for cp in self.coverpoint_l:
            ret.add_coverpoint(cp.clone())
        
        for cr in self.cross_l:
            ret.add_coverpoint(cr.clone())
            
        return ret
        