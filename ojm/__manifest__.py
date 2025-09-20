# -*- coding: utf-8 -*-
{
    'name': "Odoo Journal Manager",

    'summary': """
        This module serves to manage scientific articles publishing pipeline
        for submission, peer review, production to payment.
    """,

    'description': """
        This module serves to manage scientific articles publishing pipeline
        for submission, peer review, production to payment.
    """,

    'author': "@dess",
    'website': "http://www.monadeware.com",

    'category': 'Publishing',
    'version': '0.1',

    'depends': ['website', 'portal', 'sale_management', 'payment'],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'reports/submission_review.xml',
        'reports/review_comments.xml',
        'reports/reports.xml',
        'data/jobs.xml',
        'data/article_sequence.xml',
        'data/article_revision_sequence.xml',
        'data/journal_sequence.xml',
        'data/default_images.xml',
        'data/submission_rules.xml',
        'data/article_types.xml',
        'data/article_file_types.xml',
        'data/email_template_submission.xml',
        'data/email_invite_reviewer.xml',
        'data/email_notif_submission_editor.xml',
        'data/email_notif_review_completed.xml',
        'data/email_notif_revision_start.xml',
        'data/email_notif_partial_review.xml',
        'data/author_declarations.xml',
        'data/reviewer_reminder_email.xml',
        # backend views
        'views/backend/article_views.xml',
        'views/backend/revisions_views.xml',
        'views/backend/article_type_views.xml',
        'views/backend/article_file_type_views.xml',
        'views/backend/journal_volume_views.xml',
        'views/backend/journal_section_views.xml',
        'views/backend/journal_views.xml',
        'views/backend/journal_authors_views.xml',
        'views/backend/journal_reviewers_views.xml',
        'views/backend/submission_rule_views.xml',
        'views/backend/journal_category_views.xml',
        'views/backend/editor_views.xml',
        'views/backend/editor_position_views.xml',
        # 'views/backend/orcid_token_views.xml',
        'views/backend/author_declaration_views.xml',
        'views/backend/reviewer_invitation_views.xml',
        'views/backend/reviewer_assignment_views.xml',
        'views/backend/menu.xml',
        # frontend views
        'views/frontend/web/journals_page.xml',
        'views/frontend/web/journal_home.xml',
        'views/frontend/web/journal_issue_page.xml',
        'views/frontend/web/journal_archive.xml',
        'views/frontend/web/journal_about.xml',
        'views/frontend/web/article_page.xml',
        'views/frontend/web/all_publications.xml',
        'views/frontend/web/article_pdf_reader_page.xml',
        'views/frontend/web/user_portal.xml',
        'views/frontend/web/manuscript_form.xml',
        'views/frontend/web/thankyou.xml',
        'views/frontend/web/header_custom.xml',
        'views/frontend/web/custom_auth.xml',
        'views/frontend/web/account.xml',
        'views/frontend/web/user_portal.xml',

        'views/frontend/ojm/base_templates.xml',
        'views/frontend/ojm/portal_home.xml',
        'views/frontend/ojm/author_home.xml',
        'views/frontend/ojm/reviewer_home.xml',
        'views/frontend/ojm/reviewer_invitations.xml',
        'views/frontend/ojm/reviewer_invitation_details.xml',
        'views/frontend/ojm/reviewer_assignments.xml',
        'views/frontend/ojm/reviewer_assignments_completed.xml',
        'views/frontend/ojm/reviewer_assignment_details.xml',
        'views/frontend/ojm/journal_overview.xml',
        'views/frontend/ojm/instructions_for_authors.xml',
        'views/frontend/ojm/instructions_for_reviewers.xml',
        'views/frontend/ojm/journal_contact.xml',
        'views/frontend/ojm/submission_form.xml',
        'views/frontend/ojm/submission_edit.xml',
        'views/frontend/ojm/submission_form_preview.xml',
        'views/frontend/ojm/portal_incomplete_submissions.xml',
        'views/frontend/ojm/portal_back_to_author.xml',
        'views/frontend/ojm/submission_details.xml',
        'views/frontend/ojm/insubmission_prev.xml',
        'views/frontend/ojm/reviewer_comments.xml',
        'views/frontend/ojm/submission_in_process.xml',
        'views/frontend/ojm/submission_in_revision.xml',
        'views/frontend/ojm/revision_details.xml',
        'views/frontend/ojm/submission_saved.xml',
    ],
    

    'assets':{
        'web.assets_frontend':[
            'ojm/static/src/scss/main.scss',
            'ojm/static/src/scss/custom_auth.scss',
            'https://cdn.jsdelivr.net/npm/sticksy/dist/sticksy.min.js',
            'ojm/static/src/libs/owl/dist/owl.carousel.min.js',
            'ojm/static/src/libs/owl/dist/assets/owl.carousel.min.css',
            "https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css",
            "https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js",
            'ojm/static/src/js/main.js',
        ],
        'web.assets_qweb': [
            'ojm/static/src/xml/base_diagram.xml',
        ],
        'web.assets_backend': [
            'ojm/static/src/scss/diagram_view.scss',
            'ojm/static/src/js/vec2.js',
            'ojm/static/src/js/graph.js',
            'ojm/static/src/js/diagram_model.js',
            'ojm/static/src/js/diagram_controller.js',
            'ojm/static/src/js/diagram_renderer.js',
            'ojm/static/src/js/diagram_view.js',
            'ojm/static/src/js/view_registry.js',
            'ojm/static/src/scss/main_backend.scss',
        ],
    },


    'demo': [
        'demo/demo.xml',
    ],
}
