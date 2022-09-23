## v1.6.5 (2022-09-23)

### Fix

- **eram_visuals_wrapper.py**: Small code improvement for better maintainability

## v1.6.4 (2022-09-23)

### Fix

- **summary_evolution_csv_exporter**: Fixed logic (and tests) so that csv has no spaces between columns and values are rounded up
- **eram_visuals_wrapper.py**: Paths as strings
- wrap options between commas
- **eram_visuals_wrapper.py**: Paths as posix
- **summary_evolution_csv_exporter**: We now return the string values in the csv between commas

## v1.6.3 (2022-09-14)

### Fix

- Fixed script so its not data-dependent (#17)

## v1.6.2 (2022-09-13)

### Fix

- Exporter was splitting programs with commas in the name
- Fixed script so its not data-dependent

## v1.6.1 (2022-09-12)

### Fix

- **eram_visuals_wrapper.py**: Fixed run method to properly set the command when no platform was found
- **eram_visuals.R**: Added missing dependency

## v1.6.0 (2022-09-10)

### Feat

- We now retrieve the rscript path from the environment variables instead of hardcoded paths
- **externals/ERAMVisuals**: Adapted code to run through command line. Adapted tests
- Made R script into standalone script which takes arguments from the command line

## v1.5.1 (2022-09-09)

### Fix

- **eram_visuals_wrapper.py**: Rename file only if it actually exists (duh)
- allow 'missing_ok' to silence filenotfounderror while unlinking files
- **eram_visuals_wrapper.py**: Replacement of backup when required was not happening correctly
- Replaced the use of the statistics mean library as its giving issues in the server
- Made the mean calculation based on explicit lists

## v1.5.0 (2022-09-09)

### Feat

- Exposed the media folder so the generated evolution summary resources can be reached

## v1.4.1 (2022-09-08)

### Fix

- Removed wrong import

## v1.4.0 (2022-09-08)

### Feat

- **summary_serializer.py**: Added logic to execute the r snippet and tests to validate its correct functioning
- Corrected summaryEvolutionSerializer as the average should be average of program evo questions for a user, then for its organization, then for the whole set of organizations
- Added exporter for serialized evolution data into CSV

## v1.3.0 (2022-09-07)

### Feat

- We now import multiple references for a program

## v1.2.0 (2022-09-07)

### Feat

- Created endpoint for evolution-graph, which will call to the R script and generate a new evolution graph for all organizations
- **views.py**: It is now no longer needed to provide a useless 'pk' when requesting summaries for either linkages or evolution
- **summary_serializer.py**: Added logic to summarize evolution questions
- Added new endpoint for generating linkages summary in a json format

## v1.1.0 (2022-07-01)

### Feat

- Replace yes/no with agreement options.
- Refactor code to replace yes/no question-answer to a 'agreement' range of answers

## v1.0.0 (2022-06-24)

### Feat

- postgresql replaces the previous sqlite database

## v0.28.0 (2022-06-21)

### Feat

- downloadable reports (#75)
- **epic_answers.py**: We now list a summary of selected programs
- **views.py;serializers/report_serializer.py;models/epic_answers.py**: It is now possible to get a detailed summary of each question based on their (sub)type
- **serializers/progress_serializer.py;views.py;urls.py**: Added end point from /api/program/id/progress to retrieve the progress for the current logged in epic user, added serializer and adapted tests
- **epic_app/serializers/answer_serializer.py;epic_app/views.py**: We can now patch selected programs, adapted tests
- **epic_app/views.py**: Edited partial_update to allow admin to change values
- **views.py**: We now assign a valid serializer when creating answers from the endpoint /api/answer/
- **views.py**: Streamlined get-list get-detail (get / retrieve) for answers. Adapted tests
- **views.py**: API Client can now retrieve a serialized answer for a question without knowing either type
- **views.py**: Added endpoint for flat questions
- **generate_entity_admin.py**: Allow display of users in an organization
- **epic_app/admin_models/generate_entity_admin.py**: We can now generate epic users from the organization page
- **views.py;epic_user_serializer.py**: Added logic to update user's password
- **epic_app/serializers/epic_user_serializer.py**: Added serializer for EpicOrganization. Adapted and extended related tests
- **epic_app/models/epic_user.py**: Added organization as a model. Adapted setup and tests
- **epic_app/admin.py;epic_app/models.py;epic_app/templates/**: Added simple logic to enable future CSV importing of Areas, added templates
- **epic_app/models.py;epic_app/serializers.py;epic_app/views.py**: Added logic to serialize all data with their nested relationships
- **epic_app/models.py**: Extended logic so that clusters can be made
- **epic_app/admin.py**: Added relationships between area-group-program-question
- **settings.py**: Added middleware CORS to allow ui / backend communication with the /api/ url
- **epic_app/serializers.py**: Fixed posting answers through the browser regardless of the logged in user
- **epic_app/serializers.py**: Now the users api browser will not display the password which will be validated and required on post
- **epic_app/**: Changed serializers and views to require authentication for get / post data
- **epic_app/models.py**: Replaced cross-reference tables with single Answer and two foreign keys; adapted views and serializers
- **epic_core/urls.py**: Stable urls just for epicuser table
- **epic_app/urls.py**: Added routing for the epic_app rest calls
- **epic_app/views.py**: Added ViewSet for all the existing serialized models
- **serializers.py**: Added JSON serializers
- **migrations/models.py**: Created basic models and cross-reference tables to be modified in the admin page
- **poetry**: Added poetry as package handler
- Small markdown fix
- Small markdown fix
- Small markdown fix

### Fix

- **epic_app/importers/xlsx/**: improved import by delegating validation to each method for better error handling
- **epic_app**: Removed outdated reference to previous serializers / views
- **epic_app/admin.py**: Minor syntax fix
- **epic_app/serializers.py**: Fixed usage of wrong fields in the serializers
- **epic_app/serializers.py**: corrected typo

### Refactor

- **views.py;urls.py**: Removed previous 'questions' viewsets as the 'QuestionViewSet' replaces the whole set.
- **epic_app/admin_models**: Moved admin models to different module for better maintenance of the django tree.

## v0.27.1 (2022-06-13)

## v0.27.0 (2022-06-01)

### Feat

- **report_pdf.py**: Fixed layout

## v0.26.0 (2022-06-01)

### Feat

- **report_pdf.py**: Now the linkages report contains names instead of id's
- **report_pdf.py**: Improved report layout
- **report_pdf.py**: Improved report layout

## v0.25.0 (2022-05-31)

### Feat

- downloadable reports (#75)

## v0.24.0 (2022-05-25)

### Feat

- **epic_app/tests/test_rest_framework_url.py**: Enabled retrieve call for a pdf report; adapted test
- **commands/**: Added commands to generate dummy users and do a simple import of all the domain xlsx files

## v0.23.0 (2022-05-23)

### Fix

- **deploy.sh**: Corrected typo

### Feat

- **epic_setup.py**: Now we can generate a 'clean' start without dummy users

## v0.22.0 (2022-05-17)

### Feat

- **xlsx/domain_importer.py;models.py;program_serializer.py**: Added new fields for Program

## v0.21.1 (2022-05-13)

### Fix

- **epic_app/importers/xlsx/**: improved import by delegating validation to each method for better error handling

## v0.21.0 (2022-05-11)

### Feat

- **epic_app/models/epic_user.py**: Added is_advisor property for EpicUsers, adapted related code

## v0.20.0 (2022-05-10)

### Feat

- **epic_answers.py**: We now list a summary of selected programs
- **views.py;serializers/report_serializer.py;models/epic_answers.py**: It is now possible to get a detailed summary of each question based on their (sub)type

## v0.19.0 (2022-05-06)

### Feat

- **serializers/progress_serializer.py;views.py;urls.py**: Added end point from /api/program/id/progress to retrieve the progress for the current logged in epic user, added serializer and adapted tests

## v0.18.0 (2022-05-04)

### Feat

- **epic_app/serializers/answer_serializer.py;epic_app/views.py**: We can now patch selected programs, adapted tests
- **epic_app/views.py**: Edited partial_update to allow admin to change values
- **views.py**: We now assign a valid serializer when creating answers from the endpoint /api/answer/
- **views.py**: Streamlined get-list get-detail (get / retrieve) for answers. Adapted tests
- **views.py**: API Client can now retrieve a serialized answer for a question without knowing either type
- **views.py**: Added endpoint for flat questions

### Refactor

- **views.py;urls.py**: Removed previous 'questions' viewsets as the 'QuestionViewSet' replaces the whole set.

## v0.17.0 (2022-05-03)

### Feat

- **generate_entity_admin.py**: Allow display of users in an organization
- **epic_app/admin_models/generate_entity_admin.py**: We can now generate epic users from the organization page
- **views.py;epic_user_serializer.py**: Added logic to update user's password
- **epic_app/serializers/epic_user_serializer.py**: Added serializer for EpicOrganization. Adapted and extended related tests
- **epic_app/models/epic_user.py**: Added organization as a model. Adapted setup and tests

### Refactor

- **epic_app/admin_models**: Moved admin models to different module for better maintenance of the django tree.

## v0.16.0 (2022-04-29)

### Feat

- **epic_app/importers/xlsx_question_importer.py**: Fixed question importer to include the group as a filtering condition
- **epic_app/importers**: We now import xlsx files instead of csv to make it more straightforward for end users

### Refactor

- **importers/xlsx**: Moved xlsx importers to its own module for better maintainance.

## v0.15.0 (2022-04-20)

### Fix

- **epic_answers.py**: fixed integrity check for base question after end-to-end testing.

### Feat

- **epic_answers.py;epic_questions.py**: Added constraints to answers so only specified question types can be added

## v0.14.0 (2022-04-19)

### Feat

- **epic_app/models/epic_questions.py**: Added Key Agency Actions table
- **answer_serializer.py**: Fixed posting answers
- **epic_app/views.py**: Changed views for answers so it's possible to post as an user or an admin

### Fix

- **epic_questions.py**: Fixed meta inheritance on questions to allow unique relationships

### Refactor

- **answer_serializer.py**: Removed serializer for raw answer as it is not necessary anymore
- **epic_answers**: Split answers from questions

## v0.13.0 (2022-04-15)

### Feat

- **epic_app/admin.py**: Added admin action to generate all linkages from available programs
- **epic_app/admin.py**: Added admin views to import national framework and evolution questions
- **question_csv_importer.py**: Added csv importers for NationalFrameworkQuestion and EvolutionQuestion

### Refactor

- **importers**: Extracted each importer in a separate file for better consistency
- **importers**: Moved importers into a separate directory to allow better maintainance

## v0.12.1 (2022-04-15)

### Refactor

- **views.py**: Improved EpicUserViewSet class definition; Extended related GET - detail test.

## v0.12.0 (2022-04-15)

### Feat

- **epic_app/views.py;question_serializer.py**: We now expose a get to get (all/detail) a question category for a given program
- **epic_app/urls.py;epic_app/serializers/question_serializer.py**: We now expose each question category individually
- **epic_app/serializers/epic_user_serializer.py**: Now we expose the list of selected programs for a given user
- **epic_app/models/epic_user.py**: Extended user definition to include list of selected programs

## v0.11.0 (2022-04-11)

### Feat

- **epic_app/serializers/answer_serializer.py**: Extended answer serializer definition to match question types
- **epic_app/models/epic_questions.py**: Now questions return a new (or existing) answer for the requested user. Added tests
- **epic_app/models/epic_questions.py**: Added answer types

## v0.10.0 (2022-04-08)

### Feat

- **epic_app/serializers/question_serializer.py**: Improved serializer so we have information of its subtypes directly
- **epic_app/models/epic_questions.py**: Added one-to-one constraint for linkages question by overriding the default save method
- **epic_app/models/epic_questions.py**: Added class for questions and created one model class per type from the mockups

### Refactor

- **epic_app/serializers**: Moved serializers into different directory to better maintain them
- **epic_app/models**: Moved models into separate directory for better maintainability

## v0.9.0 (2022-04-06)

### Feat

- **epic_app/importers.py**: Now we properly import the descriptions

## v0.8.0 (2022-04-06)

### Feat

- **epic_app/serializers.py**: Exposed description for programs

## v0.7.1 (2022-04-06)

### Fix

- **epic_app/serializers.py**: Fixed agency attribute for program serializer

## v0.7.0 (2022-04-06)

### Refactor

- **epic_app/importers.py**: modified agency null (should be blank) attribute, refactored importer code to reduce duplicity

### Feat

- **epic_app/importers.py;epic_app/models.py**: Added import csv functionality
- **epic_app/admin.py**: Added agency admin to import csv, adjusted tests
- **epic_app/models.py**: Updated program to include description and a unique name case-insensitive attribute
- **epic_app/models.py;epic_app/serializers.py**: Added Agency as a model and serializer, a cluster of programs

## v0.6.0 (2022-04-05)

### Refactor

- **epic_app/importers.py**: Extracted import logic for better maintainabilit

### Feat

- **epic_app/admin.py**: Added basic import functionality
- **urls.py**: Added redirection for the admin page
- **epic_app/urls.py**: We now directly redirect the default path to /api

## v0.5.0 (2022-03-23)

### Feat

- **epic_app/admin.py;epic_app/models.py;epic_app/templates/**: Added simple logic to enable future CSV importing of Areas, added templates

## v0.4.0 (2022-03-23)

### Feat

- **epic_app/models.py;epic_app/serializers.py;epic_app/views.py**: Added logic to serialize all data with their nested relationships
- **epic_app/models.py**: Extended logic so that clusters can be made
- **epic_app/admin.py**: Added relationships between area-group-program-question

## v0.3.0 (2022-03-23)

### Feat

- **settings.py**: Added middleware CORS to allow ui / backend communication with the /api/ url

## v0.2.0 (2022-03-22)

### Feat

- **epic_app/serializers.py**: Fixed posting answers through the browser regardless of the logged in user
- **epic_app/serializers.py**: Now the users api browser will not display the password which will be validated and required on post
- **epic_app/**: Changed serializers and views to require authentication for get / post data
- **epic_app/models.py**: Replaced cross-reference tables with single Answer and two foreign keys; adapted views and serializers

### Fix

- **epic_app**: Removed outdated reference to previous serializers / views
- **epic_app/admin.py**: Minor syntax fix

## v0.1.0 (2022-03-21)

### Fix

- **epic_app/serializers.py**: Fixed usage of wrong fields in the serializers
- **epic_app/serializers.py**: corrected typo

### Feat

- **epic_core/urls.py**: Stable urls just for epicuser table
- **epic_app/urls.py**: Added routing for the epic_app rest calls
- **epic_app/views.py**: Added ViewSet for all the existing serialized models
- **serializers.py**: Added JSON serializers
- **migrations/models.py**: Created basic models and cross-reference tables to be modified in the admin page
- **poetry**: Added poetry as package handler
- Small markdown fix
- Small markdown fix
- Small markdown fix
