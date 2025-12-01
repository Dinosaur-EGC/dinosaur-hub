## 1.2.0 (2025-12-01)

### Feat

- ✨ Add Docker Build Check and Wiki Link Checker workflows
- ✨ Add security audit workflow
- ✨ Unify and optimize CI workflows
- ✨ Add Git configuration for commitizen action
- ✨ Add Commitizen configuration and bump version workflow
- metodos para subir desde zip o github refactorizados
- coptyToClipboard arreglada para csv
- Descargar csv individual arreglado
- Mejora de la vista de los csv con Papa Parse
- Ver los detalles de los csv
- actualizar view_dataset con los csv
- refactorizar routes del módulo dataset
- refactorizar forms del módulo dataset
- refactorizar servicio del módulo dataset
- adaptar upload_dataset a archivos CSV
- adaptar view_dataset a archivos CSV
- nuevos ejemplos de CSV
- dataset service actualizado con fossils
- formulario de dataset actualizado con fossils
- nuevas migraciones para incorporar Fossils
- ejemplos de csv añadidos
- actualizar el seeder de Dataset a Fossils
- columnas DOI y tags añadidas a las métricas de Fossils
- base del módulo Fossils
- fossils migration
- Module Fossils
- **test**: Add unit tests for the trending services
- **ui**: add sidebar navigation link for Trending page
- **ui**: add styling for trending cards, featured highlight, and mini-card separators
- **ui**: add full trending datasets page with filters and dynamic list container
- **ui**: add compact trending datasets preview card to public layout
- **routes**: add public trending page and preload top datasets
- **ui**: add interactive trending datasets widget

### Fix

- 🐛 Correct syntax for conditional check in CI workflow
- 🐛 Downgrade `actions/checkout` version to v4 for compatibility
- argumento de la llamada a create corregido
- argumento de la llamada a create_new_deposition corregido
- Arreglo de las migraciones
- generar 12 FossilsFiles de ejemplo
- actualizar completamente el public/routes con Fossils
- cambiar featureModel por Fossils en el módulo Zenodo
- cambiar featureModel por Fossils en el módulo explore
- featureModel completamente desvinculado
- congruencias con Fossils en fakenodo
- congruencias con Fossils en public/routes
- congruencias con Fossils en el módulo hubfile
- congruencias con Fossils en el módulo dataset
- syntax error in fossils models
- **services**: resolved indentation error

## 1.1.0 (2025-12-01)

### Feat

- ✨ add Commitizen configuration for conventional commits
- ✨ add CI workflows for linting, testing, and security audits
- ✨ add AI-powered issue summarization workflow
- codeql añadido al workflow
- **migrations**: ✨ add 'deposition' table and 'totp_secret' column to 'user' table
- **migrations**: ✨ add initial migration for database schema setup
- Workflow codacy
- ✨ Update application name and logo references
- **fakenodo**: ✨ add initial script for fakenodo module
- **fakenodo**: ✨ add initial script for fakenodo module
- **fakenodo**: ✨ add initial script for fakenodo module integration
- **migrations**: ✨ Add 'totp_secret' column to 'user' table and drop 'deposition' table
- **fakenodo**: ✨ add initial script for fakenodo module integration
- 2FA implementado
- **configuration**: ✨ add USE_FAKENODO flag for Fakenodo integration
- **tests**: ✨ add initial test files for Fakenodo module
- **fakenodo**: ✨ implement Fakenodo module with upload and management features
- **dataset**: ✨ integrate Fakenodo service for dataset uploads
- **dataset**: ✨ enhance author management in dataset upload
- **dataset**: ✨ add user upload information to dataset display
- **dataset**: ✨ add filter method to retrieve datasets with dynamic criteria
- **dataset**: ✨ add method to retrieve datasets by user ID
- **dataset**: ✨ update user link to profile view
- **profile**: ✨ add user profile view template
- **profile**: ✨ add method to retrieve user profile by user ID
- **profile**: ✨ add user profile view route

### Fix

- corrección en la ruta de la imagen del README
