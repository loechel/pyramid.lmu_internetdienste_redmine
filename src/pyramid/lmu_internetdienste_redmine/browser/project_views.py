# -*- coding: utf-8 -*-

import deform.widget

import ipdb

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from ..config import logger
from ..config import __redmine_config as redmine_config
from ..config import __redmine as redmine
from ..interfaces.webproject import IRedmineFionaUpdateProjects
from ..interfaces.webproject import IRedmineWebProject
from ..interfaces.webproject import IRedmineMilestoneProject
from ..interfaces.webproject import ITicketSchema

from ..utils import update_redmine_projects_with_fiona_dump
from ..utils import setup_webproject

from .layouts import Layouts


class RedmineBaseView(Layouts):

    def __init__(self, request):
        self.request = request

    @property
    def reqts(self):
        return {'css': None, 'js': None}


class RedmineGenericViews(RedmineBaseView):

    @view_config(
        route_name='home',
        renderer='templates/home.pt')
    def home_view(self):
        return {}


class RedmineProjectView(RedmineBaseView):

    @property
    def redmineproject_form(self):
        schema = IRedmineWebProject()
        return deform.Form(schema, buttons=('submit',))

    #@property
    def redminemilestoneproject_form(self, project_id):
        schema = IRedmineMilestoneProject()
        project_schema = schema.get('project')

        m01_schema = schema.get('milestone_01_playlandphase')
        #ipdb.set_trace()
        m01_schema.add(ITicketSchema().get('activate'))
        #project_schema.default = project_id
        #ipdb.set_trace()
        return deform.Form(schema, buttons=('submit',))

    @view_config(
        route_name='projects_view',
        renderer='templates/projects_view.pt')
    def redmineproject_view(self):
        return dict(projects=redmine.project.all())

    @view_config(
        route_name='project_add',
        renderer='templates/project_add.pt')
    def project_add(self):
        form = self.redmineproject_form.render()

        if 'submit' in self.request.params:
            controls = self.request.POST.items()

            #ipdb.set_trace()

            #while True:
            #    self.request.response.write('Test')
            #    self.request.response.flush()

            try:
                appstruct = self.redmineproject_form.validate(controls)
            except deform.ValidationFailure as e:
                # Form is NOT valid
                return dict(form=e.render())

            project = setup_webproject(
                project_name=appstruct['name'],
                project_identifier=appstruct['identifier'],
                project_parent_id=int(appstruct['parent']),
                project_description=appstruct.get('description', ''),
                project_homepage=appstruct.get('homepage', ''),
                project_status=appstruct.get('status', ''),
                project_lang=appstruct.get('lang', ''),
            )

            return HTTPFound(project.url)

        return dict(form=form, title="Add Webproject")

    @view_config(
        route_name='project_add_milestones',
        renderer='templates/project_add_milestones.pt')
    def project_add_milestones_view(self):
        pid = self.request.matchdict['id']
        project = redmine.project.get(pid)

        form = self.redminemilestoneproject_form(pid).render()

        if 'submit' in self.request.params:
            controls = self.request.POST.items()

            #ipdb.set_trace()

            #while True:
            #    self.request.response.write('Test')
            #    self.request.response.flush()

            try:
                appstruct = self.redminemilestoneproject_form(pid).validate(controls)
            except deform.ValidationFailure as e:
                # Form is NOT valid
                return dict(form=e.render())

            ipdb.set_trace()
            #add_milestone_initialgespraech(project=project,)

            return HTTPFound(project.url)

        return dict(form=form, title="Add Milestone to Webproject")

    @view_config(
        route_name='project_view',
        renderer='templates/project_view.pt')
    def projectpage_view(self):
        id = self.request.matchdict['id']
        project = redmine.project.get(id)

        ipdb.set_trace()

        return dict(project=project)


class RedmineFionaUpdateProjectView(RedmineBaseView):

    @property
    def update_projects_form(self):
        schema = IRedmineFionaUpdateProjects()
        return deform.Form(schema, buttons=('submit',))

    @property
    def reqts(self):
        return self.update_projects_form.get_widget_resources()

    @view_config(route_name='update_fiona_projects',
                 renderer='templates/update_fiona_projects.pt')
    def update_projects(self):
        form = self.update_projects_form.render()

        if 'submit' in self.request.params:
            controls = self.request.POST.items()
            try:
                appstruct = self.update_projects_form.validate(controls)
            except deform.ValidationFailure as e:
                # Form is NOT valid
                return dict(form=e.render())
            input_file = appstruct['csv_file']

            logger.info('process file: ' + input_file['filename'])

            update_redmine_projects_with_fiona_dump(input_file['fp'])

            #return "Successful"
            #return HTTPFound(project.url)

        return dict(form=form)
