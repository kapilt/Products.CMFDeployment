##################################################################
#
# (C) Copyright 2002-2004 Kapil Thangavelu <k_vertigo@objectrealms.net>
# All Rights Reserved
#
# This file is part of CMFDeployment.
#
# CMFDeployment is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# CMFDeployment is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CMFDeployment; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##################################################################
"""
Purpose: read an xml serialization of a deployment policy into python objects
Author: kapil thangavelu <k_vertigo@objectrealms.net> @2002-2004
$Id$
"""

from xml.sax import make_parser, ContentHandler
from UserDict import UserDict

from ZPublisher.mapply import mapply
from Products.CMFDeployment import pipeline, dependencies


marker = []
class PolicyNode(UserDict):
    reserved = ('data',)

    def __hasattr__(self, name):
        v = self.__dict__.get(name, marker)
        if v is marker:
            return self.data.has_key(name)
        return True

    def __getattr__(self, name):
        v = self.__dict__.get(name, marker)
        if v is marker:
            return self.data[name]
        return v
    
    def __setattr__(self, name, value):
        if name in PolicyNode.reserved:
            self.__dict__[name]=value
        else:
            self.data[name]=value
    
class MetaReader(ContentHandler):

    def __init__(self):

        self.buf = []
        self.prefix = ''
        self.stack = []
        
    def startElement(self, element_name, attrs):
        name = element_name.lower()
        if self.prefix: name = '%s%s'%(self.prefix, name.capitalize())      
        method = getattr(self, 'start%s'%name.capitalize(), None)

        # get rid of unicode
        d = {}
        for k, v in attrs.items():
            d[str(k)]= str(v)
        
        if method: 
            apply(method, (d,))

    def endElement(self, element_name):
        chars = str(''.join(self.buf)).strip()
        self.buf = []

        name = element_name.lower()
        
        if self.prefix: name = '%s%s'%(self.prefix, name.capitalize())            
        method = getattr(self, 'end%s'%name.capitalize(), None)
        
        if method: 
            apply(method, (chars,))
         
    def characters(self, chars):
        self.buf.append(chars)


class PolicyReader(MetaReader):

    def startDeploymentpolicy(self, attrs):
        self.policy = PolicyNode(attrs)

    def startIdentification(self, attrs):
        self.policy.ident = PolicyNode(attrs)
        self.prefix = 'Ident'

    def endIdentidentification(self, chars):
        self.prefix =''

    def startIdentfilter(self, attrs):
        filters = self.policy.ident.setdefault('filters', [])
        filter = PolicyNode(attrs)
        filters.append(filter)

    def startOrganization(self, attrs):
        organization = PolicyNode(attrs)
        organization['restricted']=[]
        self.policy.organization = organization
        self.prefix='Organization'

    def startOrganizationrestricted(self, attrs):
        restricteds = self.policy.organization.setdefault('restricted', [])
        restricteds.append(attrs['id'])

    def startOrganizationcomposite(self, attrs):
        composites = self.policy.organization.setdefault('composites', [])
        composites.append(attrs['type'])

    def endOrganizationorganization(self, chars):
        self.prefix=''
        
    def startMastering(self, attrs):
        mastering = PolicyNode(attrs)
        self.policy.mastering = mastering
        self.prefix='Mastering'

    def endMasteringmastering(self, chars):
        self.prefix=''
        
    def startMasteringmime(self, attrs):
        mimes = self.policy.mastering.setdefault('mimes', [])
        mime = PolicyNode(attrs)
        if mime.has_key('ghost'):
            mime['ghost'] = int(mime.ghost)
        mimes.append(mime)

    def startSkins(self, attrs):
	skins = PolicyNode(attrs)
	self.policy.skins = skins
	self.prefix='Skins'
        self.policy.skins.setdefault('directories',[])

    def startSkinsdirectory(self, attrs):
	dirs = self.policy.skins.setdefault('directories', [])
	sd = PolicyNode(attrs)
	dirs.append(sd)

    def endSkinsskins(self,attrs):
	self.prefix=''

    def startStrategy(self, attrs):
        self.policy.strategy = PolicyNode(attrs)

    def startUris(self, attrs):
        self.policy.uris = PolicyNode(attrs)

    def startChain_user(self, attrs):
        self.policy.chain_user = PolicyNode(attrs)
	
    def getPolicy(self):
        return self.policy
        
def read_policy(file):
    # file = file handle
    parser = make_parser()
    reader = PolicyReader()
    parser.setContentHandler(reader)
    parser.parse(file)
    return reader.getPolicy()

REMAP_TYPES = ( ( 'CMFDeployment', 'addContentRule' ),
                ( 'CMFDeployment', 'addMimeMapping' ), )
                

DEFAULT_RULE_PRODUCT = 'CMFDeployment'    
DEFAULT_RULE_FACTORY = 'addContentRule'
DEFAULT_RULE_FACTORY_MAP = {
    'ext_expr':'extension_expression',
    'filter_expr':'condition'
    }

def remap_default_rule_factory( m ):
    delk = []
    for key, factory_key in DEFAULT_RULE_FACTORY_MAP.items():
        value = m.get(key, '')
        m[factory_key] = value
        delk.append(key)

    for dk in delk:
        del m.data[dk]

    return m

def make_policy(portal, policy_node, id=None, title=None):
 
    import DefaultConfiguration
    from App.Common import package_home

    deployment_tool = portal.portal_deployment
    catalog_tool    = portal.portal_catalog
    
    if id:
        title = title or ''
        deployment_tool.addPolicy( id, title )
    else:
        id = policy_node.id
        deployment_tool.addPolicy( policy_node.id, policy_node.id)
        
    policy = getattr(deployment_tool, id)
    
    identification = getattr(policy, DefaultConfiguration.ContentIdentification)
    if hasattr(policy_node.ident, 'filters'):
        for f in policy_node.ident.filters:
            identification.filters.addFilter(f.id, f.expr)


    ## mastering setup
    mastering = getattr(policy, DefaultConfiguration.ContentMastering)    
    
    for m in policy_node.mastering.mimes:
        # transparently map old policies to the expected format
        product = m.get('product', DEFAULT_RULE_PRODUCT)
        factory = m.get('factory', DEFAULT_RULE_FACTORY)
        import pprint
        print 'ee', product, factory
        pprint.pprint(dict(m.items()))
        
        if (product, factory) in REMAP_TYPES:
            print 'remapped'
            m.setdefault('ghost',0)
            m = remap_default_rule_factory( m )

        pprint.pprint( dict( m.items() ) )
            
        factory = getattr(mastering.mime.manage_addProduct[product], factory)
        md = dict(m)
        if 'product' in md: del md['product']
        if 'factory' in md: del md['factory']
        factory( **md )
        #mapply(factory, keyword=m)
        
    ## chain stuff
    deployment_skin = policy_node.mastering.skin.strip()
    
    if deployment_skin:
        mastering.editSkin(enable=1, skin_name=deployment_skin)

    if policy_node.has_key('chain_user'):
        mastering.site_user.edit(enable=1,
                                 user=policy_node.chain_user.user,
                                 udb_path=policy_node.chain_user.udb_path)        

    ## org setup
    organization = getattr(policy, DefaultConfiguration.ContentOrganization)

    fs_mount = policy_node.organization.fs_mount
    
    if fs_mount.startswith('*'): # a little trick for the example
        cmfdeploydir = package_home(globals())
        fs_mount = fs_mount.replace('*', cmfdeploydir)
        
    organization.structure.setMountPoint(fs_mount)
    organization.structure.setCMFMountPoint(policy_node.organization.cmf_mount)
    
    if policy_node.organization.has_key('restricted'):
        organization.structure.setRestrictedPoints(policy_node.organization.restricted)

    if policy_node.organization.has_key('composites'):
        organization.structure.setCompositeDocumentTypes(policy_node.organization.composites, _force=1)        

    ## uris setup
    uris = getattr(policy, DefaultConfiguration.ContentURIs)

    if policy_node.has_key('uris'):
        if policy_node.uris.has_key('target_path'):
            uris.editContentURI(target_path=policy_node.uris.target_path,
                                vhost_path=policy_node.uris.vhost_path,
                                link_error_url=policy_node.uris.link_errors
                                )
 
    ## skins setup
    directory_views = getattr(policy, DefaultConfiguration.ContentDirectoryViews)

    for sd in policy_node.skins.directories:
        id = sd.get('id', sd.view_path.replace('/',''))
	directory_views.addDirectoryViewRule(
                                id,
				sd.view_path, 
				sd.source_path, 
				sd.deploy_path
				)
  
    # strategy setup
    strategies = getattr(policy, DefaultConfiguration.DeploymentStrategy)
    if policy_node.has_key('strategy') and policy_node.strategy.has_key('id'):
        print "reader: policy_node: ", policy_node.strategy.id
        strategies.setStrategy(policy_node.strategy.id)

    #################################################################
    #ContentMap is added automatically to the policy, in DefaultConfig.py
    #idem for DependencySource, DeletionSource
    #Creates the DependencyManager
    policy_id= policy.getId()
    a_dependency_manager= dependencies.DependencyManager("DependencyManager", policy_id, catalog_tool)

    # setting up the incremental index and Create the Policy Pipeline
    steps= (pipeline.PipeEnvironmentInitializer(),
                pipeline.ContentSource(),
                pipeline.ContentPreparation(),
                pipeline.DirectoryViewDeploy(),
                pipeline.ContentProcessPipe(),
                pipeline.ContentTransport(),
                a_dependency_manager
                )
    #Create a pipeline and Add steps in it
    new_pipeline = pipeline.PolicyPipeline()
    new_pipeline.steps= steps  
    new_pipeline.process(policy)
    
    return policy
    
if __name__=='__main__':

    import sys
    import pprint
    
    policy = read_policy(sys.argv[1])

    for k,v in policy.items():
        print k
        
        for k,v in v.items():
            print "  "*5, k, v
        
    
