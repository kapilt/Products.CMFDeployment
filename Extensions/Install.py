def install(self):

    from Products.CMFDeployment import DeploymentTool

    ob = DeploymentTool.DeploymentTool()
    self._setObject(ob.getId(), ob)

    return 2
