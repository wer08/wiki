from django.shortcuts import render
from django.shortcuts import redirect
from django import forms
from django.core.files import File
import markdown2
import random

from . import util
#Form to add new entry to encyclopedia
#It contains 2 fields one for title and one for body of entry
class NewEntryForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'name':'title', 'placeholder':'Title'}))
    entry = forms.CharField(widget=forms.Textarea(attrs={'name':'entry', 'placeholder':'Markdown entry'}))

#Form to edit entry, contains one field
class EditEntryForm(forms.Form):
    entry = forms.CharField(widget=forms.Textarea(attrs={'name':'entry', 'placeholder':'Markdown entry'}))

#this function randomly chooses one title from the list of entries and redirects us to adequate page 
def random_page(request):
    entry = random.choice(util.list_entries())
    return redirect("entry",entry)


#function to edit entry
def edit(request):
    #POST method opens an md file and saves the changes when submitted
    if request.method == "POST":
        title = request.POST.get("title")
        form = EditEntryForm(request.POST)
        if form.is_valid():
            with open(f"entries/{title}.md", "w") as f:
                text = form.cleaned_data["entry"]
                entryFile = File(f)
                entryFile.write(text)
                return redirect("entry", title)
        else:
            return render(request, "encyclopedia/edit.html", {
                "form": form
            })
    #GET method displays form with current text of an entry
    title = request.GET.get("title")
    with open(f"entries/{title}.md", "r") as f:
        entryFile = File(f)
        entry = entryFile.read()
    form = EditEntryForm(initial={'entry': entry})
    return render(request, "encyclopedia/edit.html",{    
        "form": form,
        "title": title
    })
     
#function to add new entry
def add(request):
    #POST method firstly checks if there is entry with the same title as entry that we are trying to add
    #If so function renders an error page
    #If there is no entry with that title function creates an entry
    if request.method=="POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            body = form.cleaned_data["entry"]
            for entry in util.list_entries():
                if title.lower() == entry.lower():
                    return render(request, "encyclopedia/error.html", {
                        "error": "Entry already created"
                    })
            with open(f"entries/{title}.md", "w") as f:
                newEntry = File(f)
                newEntry.write(body)
            return redirect("entry",title)
        else:
            return render(request, "encyclopedia/add.html", {
            "form": form
            })
    #GET method enders a page with form
    return render(request, "encyclopedia/add.html", {
        "form": NewEntryForm()
    })

#index function renders a page with list of entries(each entry is a link to page of that entry)
def index(request):
    
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def search(request):
    q = request.GET.get('q')
    #function searched entries is used as a filter. If searched phrase exists in entry it returns true otherwise false
    def searched_entries(entry):
        if q.lower() in entry.lower():
            return True
        else:
            return False
    #Here program creates list of entries in lower case so that search function woulf be case insensitive
    entry_list = []
    for entry in util.list_entries():
        entry_list.append(entry.lower())
    
    #if searched phrase is a title of entry we get redirected to an entry page
    if q.lower() in entry_list:
        return redirect('entry',q)

    #else we filter the list using filter that we implemented before.
    #If filtered list is empty we get redirected to entry function which will display error message
    #Otherwise it displays list of all entries that contain searched phrase
    else:
        searched_filter = filter(searched_entries, util.list_entries())
        searched = list(searched_filter)
        if not searched:
            return redirect ('entry',q)

        return render(request, "encyclopedia/searched.html", {
            "entries": searched
        })
#entry function renders error page when there is no entry with given title
#otherwise it converts markdown file to html and renders an encyclopedia entry
def entry(request, title):
    if not util.get_entry(title):
        return render(request, "encyclopedia/error.html", {
            "error": "There is no such page"
        })

    try:
        entry = markdown2.markdown(util.get_entry(title))
    except TypeError:
        raise

    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "page": entry
    })