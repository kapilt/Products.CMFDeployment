"""
ROUGH DRAFT

defines the operation of the incremental pipeline for deployment.

deploying content on an incremental basis is a straight forward though
complex process. the naive initial implementation in cmfdeployment 1.0,
merely deployed content created/modified since the last deployment
run. real world experience quickly proved this to be fatally flawed for
a number of reasons.

  - content often have interdependencies that need to be modeled
    in an incremental deployment system.

  - the engine needed to process content deletions, previously the
    deployment engine dealt only with publishing.


the incremental engine uses the following components, arranged as shown
in the diagram of an execution pipeline below.

  Dependency Manager

   Responsible for processing a descriptor's specified dependencies
   and reverse dependencies to ensure their included in the deployment.

  IncrementalPolicyIndex

   A plugin zcatalog index, installed into the portal catalog, and used
   to track when a deployed piece of content is deleted, and then
   adds a deletion record to the policy's deletion source [below]

  Plugin Content Sources

   AlwaysDeployed Source

    returns content marked to be deployed every run. 

   Deletion Source

    a content source for deletion records.

   Dependency Source

    a source for deletions, as injected by the dependency manager.

   the dependency plugin content source is injected to during
   the pipeline execution. a duplicate eliminating filter needs
   to be utilized in the pipeline execution ( earlier the better ).

  Pipeline Invariant
  
    - deployed content filtered out will trigger deletion descriptor
      creation.

 ------

 Incremental Pipeline Diagram 
 
                                    catalog | deletions | dependencies
                                          +                       +
     -------- Filters --- Content Source --                       +
     +                                                            +
     +                                                            +
     +                                                            +
     +                                                            +
     +                                                            +
  Content Rules                                                   +
     +                                                            +
     +                                                            +
     +                                                            +
     +                                                            +
  Dependency Manager  ---------------------------------------------
     +
     +
  Resolver                                         +
     +                                             +
     +                                             +
     +                                             +
  ContentMap -----------------------------IncrementalIndex
  
     
$Id$
"""
