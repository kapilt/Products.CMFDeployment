"""
Purpose: Unittests for testing incremental.py
Author: Lucie LEJARD <lucie@sixfeetup.com> @2005
License: GPL
Created: 10/28/2005
$Id: $
"""
import os, sys, time

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests.PloneTestCase import PloneTestCase

ZopeTestCase.installProduct('CMFDeployment')
ZopeTestCase.installProduct('MimetypesRegistry')
ZopeTestCase.installProduct('PortalTransforms')
ZopeTestCase.installProduct('Archetypes')
ZopeTestCase.installProduct('ATContentRule')
ZopeTestCase.installProduct('ZCatalog')
ZopeTestCase.installProduct('ZCTextIndex')

from Products.CMFCore.utils import getToolByName
from Products.CMFDeployment import DeploymentProductHome
from Products.CMFDeployment.DeploymentPolicy import DeploymentPolicy
from Products.CMFDeployment.ExpressionContainer import getDeployExprContext
from Products.CMFDeployment.Descriptor import ContentDescriptor
from Products.CMFDeployment import incremental
from Products.ZCatalog import ZCatalog, Vocabulary
from Products.CMFCore.tests.base.testcase import SecurityRequestTest
from Products.ZCTextIndex.ZCTextIndex import ZCTextIndex, PLexicon
from Products.ZCTextIndex.Lexicon import Splitter
from Products.ZCTextIndex.Lexicon import CaseNormalizer, StopWordRemover
from Products.PluginIndexes.TextIndex.TextIndex import TextIndex
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.CMFCore.CatalogTool import CatalogTool
from Products.ZCatalog import ZCatalog
from Products.CMFDeployment import pipeline
from Products.CMFDeployment import dependencies
from Products.CMFDeployment import ContentMap
from Products.CMFDeployment.Descriptor import DescriptorFactory

from Products.ZHNESite import ZHNEProductHome

def setupContentTree( portal ):
    portal.portal_catalog.indexObject( portal )

    portal.invokeFactory('Folder', 'news')
    portal.news.invokeFactory('Document','index_html')
    
    news_index_content = '''\
    <html>
    <body>
    # relative url
    <a href="../about">About Us</a>

    # absolute url
    <a href="/portal/about/contact">Jobs - You Wish!</a>    

    # javascript url
    <a href="javascript:this.print()">Print Me</a>    

    # mailto url
    <a href="mailto:deployment@example.com">Print Me</a>    
    
    # test self referencing content
    <a href="./index_html"> My Self </a>
    <a href="/portal/news/index_html">My Self aliased</a>
    <a href=".">My Self</a>
    
    # test anchor link inside of page
    <a href="#furtherdown">Down the page</a>
    
    this is some more text
    
    <a name="furtherdown"></a>
    here is stuff that is further down the page.
    </body>
    </html>
    '''
    portal.news.index_html.edit(text_format='html', text=news_index_content)
    
    portal.invokeFactory('Folder', 'about') 
    portal.about.invokeFactory( 'Document', 'index_html')
    about_index_content = '''
    <html><body>
    Case Studies
    
    case studies... <a href="/portal/logo.jpg"> Logo </a>
    we eaten at millions of mcdonalds...

    Dig our Cool JavaScript 
    <javascript src="/portal/plone_javascripts.js"/>
    <img src="/portal/vera.jpg"> logo </src>
    <img src="../vera.jpg"> logo </src>   
    <a href="/portal/news/index_html">Lucie</a>
    </body>
    </html>
    '''
    portal.about.index_html.edit(text_format="html", text=about_index_content)
    portal.about.invokeFactory('Document', 'contact')
    
    portal.invokeFactory('Folder','events')
    portal.events.invokeFactory( 'Event', 'Snow Sprint')
    portal.events['Snow Sprint'].edit( 
        title='Snow Sprint',
        description="fun not in the sun",
        location="Austria, EU",
        contact_name="jon stewart",
        contact_email="dubya@dailyshow.com",
        event_url="/portal/news/index_html")
            
    portal.events.invokeFactory('Event', 'cignex_sprint')
    portal.events.cignex_sprint.edit(
        title='Cignex Sprint',
        description="fun in the fog",
        location="Austria, EU",
        contact_name="jon stewart",
        contact_email="dubya@dailyshow.com",
        event_url="http://hazmat.gov")    


class TestDependencyManager(PloneTestCase):
    
    def afterSetUp(self):
        self.loginPortalOwner()
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.installProduct('ATContentRule')
        installer.installProduct('CMFDeployment')
        
        policy_file = os.path.join(DeploymentProductHome,'examples','policies', 'plone.xml')
        fh = open( policy_file )
        deployment_tool = getToolByName(self.portal, 'portal_deployment')
        deployment_tool.addPolicy( policy_xml=fh )
        fh.close()
        self.policy = deployment_tool.getPolicy('plone_example')
        setupContentTree(self.portal)
        self.catalog_tool = getToolByName(self.portal, "portal_catalog")  
        rules = self.policy.getContentMastering().mime
        rules.manage_addProduct['ATContentRule'].addArchetypeContentRule(
            id = "at_image_content",
            condition="python: object.portal_type == 'Sample Image Content'"
            )  
        
    def testProcessRemoval(self): 
        #################################
        #Add the ContentMap to the policy
        resolver= self.policy.getDeploymentURIs()
        one_map= ContentMap.ContentMap(resolver) 
        self.policy._setOb('ContentMap', one_map)      
     
        #################################
        #Creates the dependencySource and add it to the policy
        id_dep= "pouetDepSource"
        title_dep= "The Dependency Source"
        dependency_source= dependencies.DependencySource(id_dep, title_dep)
        sources= self.policy.getContentSources()
        sources._setOb('dependency_source', dependency_source)
    
        #################################
        #Adding the deletion source to the contentIdentification
        deletion_source= incremental.DeletionSource("pouetDeletion")
        sources._setOb('deletion_source', deletion_source)
    
        #################################
        #Add an index and its name
        extra= self.policy.getId()
        self.catalog_tool.manage_addIndex('plone_example_incremental_idx', 'PolicyIncrementalIndex', extra)
        self.catalog_tool.manage_addColumn('plone_example_incremental_idx')
        #Index an object with the new index plone_example_incremental_idx
        self.catalog_tool.indexObject(self.portal.about.contact, ['plone_example_incremental_idx']) 
    
        ################################
        #Create the Policy Pipeline
        policy_id= self.policy.getId()
        catalog = self.catalog_tool
        a_dependency_manager= dependencies.DependencyManager("PouetDepManager", policy_id, catalog)
        new_steps= (pipeline.PipeEnvironmentInitializer(),
                    pipeline.ContentSource(),
                    pipeline.ContentPreparation(),
                    pipeline.DirectoryViewDeploy(),
                    pipeline.ContentProcessPipe(),
                    pipeline.ContentTransport(),
                    a_dependency_manager
                    )
        #Create a pipeline and Add steps in it
        new_pipeline = pipeline.PolicyPipeline()
        new_pipeline.steps= new_steps  
        new_pipeline.process(self.policy)
                
        #Unindex the object
        self.catalog_tool.unindexObject(self.portal.about.contact)  
        
        #################################
        #taking the content that has been deleted in deletion source
        sources= new_pipeline.services['ContentIdentification'].sources
        deletion_source = sources._getOb('deletion_source', None)
        deleted_records= deletion_source.getContent()
        
        #take the reverse dependencies of the deleted_records
        #no need to clean the deletion source and the dep. source
        #one_map.pprint()
        try:
            while (True):
                record = deleted_records.next()
                #print "\ntest pouet: record: ", record.descriptor.getContent()
                a_dependency_manager.processRemoval(record)
        except:         
            #check if dependency source and deletion source are empty
            deleted_records= deletion_source._records
            self.assertEqual(deleted_records, [], 'Deletion source should be empty')
            
            dependency_source = sources._getOb('dependency_source', None)
            dependencies_source= dependency_source._queue
            self.assertEqual(dependencies_source, [], 'Dependency Source should be empty')
        
        
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDependencyManager))
    return suite

if __name__ == '__main__':
    unittest.main()
