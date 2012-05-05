from django.db import models
from django.forms import ModelForm
from django.contrib.admin.widgets import FilteredSelectMultiple
from models import *
from django.forms.models import inlineformset_factory
from django.forms.models import BaseInlineFormSet
from django.forms.formsets import DELETION_FIELD_NAME
from django import forms
from erp_test.misc.helper import delete_this_file
from erp_test.users.models import Group
import re

# The __init__ hack is to allow blank comment strings. No error will
# be generated if they're empty, but the view will check if it is
# empty and not save it. That way, there are no form errors when a user
# decides not to add a comment and no empty comments are saved either.
class TaskCommentForm (ModelForm):
    def __init__(self, *args, **kwargs):
        super(TaskCommentForm, self).__init__(*args, **kwargs)
        self.fields['comment_string'] = forms.CharField (widget = forms.Textarea, required = False)

    class Meta:
        model = TaskComment
        exclude = ('author', 'task')

class SubTaskCommentForm (ModelForm):
    def __init__(self, *args, **kwargs):
        super(SubTaskCommentForm, self).__init__(*args, **kwargs)
        self.fields['comment_string'] = forms.CharField (widget = forms.Textarea, required = False)

    class Meta:
        model = SubTaskComment
        exclude = ('author', 'subtask')                

class UpdateForm (ModelForm):
    class Meta:
        model = Update
        exclude = ('author')

class TaskForm (ModelForm):
    # Will change the widget... Some other day :)
    # def __init__(self, *args, **kwargs):
    #     super(TaskForm, self).__init__(*args, **kwargs)
    #     print args
    #     print kwargs
    #     # self.fields['tags'] = forms.ModelMultipleChoiceField (widget = forms.Textarea, required = False)

    class Meta:
        model = Task
        exclude = ('creator', )

class CoordModelMultipleChoiceField (forms.ModelMultipleChoiceField):
    def label_from_instance(self, coord):
        return '%s' % coord.get_profile ().name

class SubTaskForm (ModelForm):
    def __init__(self, *args, **kwargs):
        super (SubTaskForm, self ).__init__(*args, **kwargs)
        # TODO : Make a default Department name appear instead of '--------'
        if 'department' in self.fields:
            # 'cos in edit_subtask form, the SubTaskForm won't
            # contain a 'department' field.
            self.fields['department'].queryset = Group.objects.filter (
                label__name = 'Department')
        # Find a way of dynamically filtering coord list according to
        # Department field's value
        self.fields['coords'] = CoordModelMultipleChoiceField (required = False, queryset = User.objects.all ())
    class Meta:
        model = SubTask
        exclude = ('creator', 'description', 'department', 'task')

class DocumentForm (ModelForm):
    class Meta:
        model = Document
        exclude = ('uploader', 'label')

class TaskDocumentForm (ModelForm):
    class Meta:
        model = TaskDocument
        exclude = ('uploader', 'task', 'label')

class SubTaskDocumentForm (ModelForm):
    class Meta:
        model = SubTaskDocument
        exclude = ('uploader', 'subtask', 'label')

SubTaskDocumentFormset = inlineformset_factory (SubTask,
                                                SubTaskDocument,
                                                form = SubTaskDocumentForm,
                                                extra = 2) 

class BaseSubTaskFormset(BaseInlineFormSet): 
    """
    Inline formset for SubTask but with nested formset for SubTask
    Documents.
    """
 
    def add_fields(self, form, index):
        """
        Add our fields to each form in the formset.
        Namely,
        - a formset for SubTask Documents and
        - a form for SubTask Comment.
        """
        # allow the super class to create the fields as usual
        super(BaseSubTaskFormset, self).add_fields(form, index)

        try:
            instance = self.get_queryset()[index]
            pk_value = instance.pk
        except IndexError:
            instance=None
            pk_value = hash(form.prefix)
 
        if self.data:
            # Note : We need form prefixes to distinguish between
            # various forms

            # Store the Document formset in the .nested property
            form.nested_docs = SubTaskDocumentFormset(data=self.data,
                                                 files = self.files,
                                                 instance = instance,
                                                 prefix = 'SUBTASKDOC_%s' % pk_value)
            # Store the Comment Form in the nested_comment property
            form.nested_comment = SubTaskCommentForm (data = self.data,
                                                      prefix = 'SUBTASKCOMMENT_%s' % pk_value)
        else:
            form.nested_docs = SubTaskDocumentFormset (instance = instance,
                                                  prefix = 'SUBTASKDOC_%s' % pk_value)
            form.nested_comment = SubTaskCommentForm (prefix = 'SUBTASKCOMMENT_%s' % pk_value)

    def my_empty_form (self):
        """
        Return empty_form for Doc Formset concatenated with empty
        Comment form.
        """
        return self.forms[0].nested_docs.empty_form


    def is_valid(self):
        print 'In is_valid'
        result = super(BaseSubTaskFormset, self).is_valid()
 
        for form in self.forms:
            if hasattr(form, 'nested_docs'):
                # Make sure each nested formset is valid as well
                print 'Document Form : ', form.nested_docs.instance, form.nested_docs.is_valid (), result
                for doc_form in form.nested_docs:
                    print 'Form - '
                    print 'Not Changed : ', not doc_form.has_changed ()
                    print 'Valid : ', doc_form.is_valid ()
                    print 'Not Changed or is Valid : ', not doc_form.has_changed () or doc_form.is_valid ()
                    print 'instance.pk : ', doc_form.instance.pk
                    if doc_form.instance.pk is not None:
                        print 'Form errors : ', doc_form.errors
                        print 'Changed data : ', doc_form.changed_data
                        print doc_form
                    result = result and (not doc_form.has_changed () or doc_form.is_valid ())
                print form.nested_docs.errors

            if hasattr (form, 'nested_comment'):
                curr_comment_form = form.nested_comment
                print 'Subtask nested Comment Form valid : ', curr_comment_form.is_valid ()
                result = result and curr_comment_form.is_valid ()
                
        print 'Is Valid : ', result
        return result

    def save_new(self, form, commit=True):
        """Saves and returns a new model instance for the given form."""
 
        print 'In save_new'
        instance = super(BaseSubTaskFormset, self).save_new(form, commit=commit)
 
        # update the form's instance reference
        form.instance = instance
 
        # update the instance reference on nested forms
        form.nested_docs.instance = instance

        # iterate over the cleaned_data of the nested formset and update the foreignkey reference
        for cd in form.nested_docs.cleaned_data:
            cd[form.nested_docs.fk.name] = instance
 
        return instance
 
    def should_delete(self, form):
        """Convenience method for determining if the form's object will
        be deleted; cribbed from BaseModelFormSet.save_existing_objects."""
 
        if self.can_delete:
            raw_delete_value = form._raw_value(DELETION_FIELD_NAME)
            should_delete = form.fields[DELETION_FIELD_NAME].clean(raw_delete_value)
            return should_delete
 
        return False
 
    def save_all(self, user, commit=True):
        """
        Save all formsets and along with their nested formsets and
        nested comment form.
        """

        print 'In save_all'
        # Save without committing (so self.saved_forms is populated)
        # -- We need self.saved_forms so we can go back and access
        #    the nested formsets
        objects = self.save(commit=False)
 
        # Save each instance if commit=True
        if commit:
            for o in objects:
                o.save()
 
        # save many to many fields if needed
        if not commit:
            self.save_m2m()
 
        # save the nested formsets
        for form in set(self.initial_forms + self.saved_forms):
            if self.should_delete(form): continue
 
            # Docs to be deleted
            for doc_form in form.nested_docs.deleted_forms:
                # From Django 1.3, FileField files won't get deleted, only
                # the model object will. So, we do it ourselves.
                delete_this_file (os.path.join (settings.MEDIA_ROOT,
                                                doc_form.instance.document.name))
            # Docs to be saved
            curr_docs = form.nested_docs.save(commit = False)
            for doc in curr_docs:
                doc.uploader = user
                if commit:
                    doc.save ()
            print 'Curr Docs : ', curr_docs

            # Save the comment form (if it isn't empty)
            if form.nested_comment.cleaned_data['comment_string'] != '':
                curr_comment = form.nested_comment.save (commit = False)
                curr_comment.author = user
                curr_comment.subtask = form.instance
                if commit:
                    curr_comment.save ()

