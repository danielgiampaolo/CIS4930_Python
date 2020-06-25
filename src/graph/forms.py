from django import forms


class nodeInput(forms.Form):
    newNode = forms.CharField(max_length=20, required=False)
    newedgefrom = forms.CharField(max_length=20, required=False)
    newedgeto = forms.CharField(max_length=20, required=False)

    # make sure information is valid
    # make sure nodes are unique (non-duplicate names)
    # implement error checking in the future

    # Currently, testing "fields" attribute to add forms

    def addNode(self, name, value):
        self.fields[name] = forms.CharField(
            max_length=20, empty_value=value
        )
        pass

    def addEdge(self, name_to, value_to, name_from, value_from):
        self.fields[name_to] = forms.CharField(
            max_length=20, empty_value=value_to
        )
        self.fields[name_from] = forms.CharField(
            max_length=20, empty_value=value_from
        )

    def delNode(self, name):
        pass

    def delEdge(self, name_to, value_to, name_from, value_from):
        pass
    # get nodes from
