## 1.6.0 (2025-12-14)

### Feat

- **routes**: 🎉 Add /version endpoint to display application version

## 1.5.0 (2025-12-14)

### Feat

- **docker**: 🎉 Add version display on startup and extract version info
- **tests**: 🎉 Add tests for user profile summary and 2FA functionality
- **tests**: 🎉 Add Selenium tests for user profile features
- **docker**: ✨ Add MARIADB_HOSTNAME environment variable for web service
- **profile**: 🎉 Add load testing and unit tests for user profile features
- **ci**: wiki-links mejorado
- **ci**: añadir reporte de enlaces rotos con issues
- Add Empty Cart
- Contador de items actualizado
- Contador del carrito
- Acceso a carrito desde base y corrección de service de Hubfile
- Vista del carrito
- Migracion de cart
- Routes de cart actualizado
- Service de cart
- Implementación de cart
- carte de Get Started actualizado
- favicon cambiado
- ✨ Add database seeding command to entrypoint script
- ✨ Add database seeding step during deployment

### Fix

- 🐛 Fix missing parentheses in `get_authenticated_user_profile` call
- arreglo de la creacion de issues en wiki-links
- parámetro arreglado de lychee
- Texto actualizado en explore/index.html
- Error en busqueda de datasets resuelto
- Arreglo mensaje BluePrint
- Download cart zip
- Arreglo de remove_item_from_cart
- refactorización del test_upload_dataset
- quitar las estadísticas de featuremodel
- aparecen los 5 datasets más descargados esa semana en el home
- hacer que el sistema rechace zips vacíos
- 🐛 Update base templates for consistency
- 🐛 Update profile templates for consistency
- 🐛 Update dataset templates for consistency
- 🐛 Update http response templates for consistency
- 🐛 Update http responses templates for consistency
- 🐛 Update rosemary commands for consistency
- 🐛 Update zenodo service for consistency
- 🐛 Update fakenodo service for consistency
- 🐛 Update dataset test_trending for consistency
- 🐛 Update dataset service for consistency
- 🐛 Update dataset models for consistency
- 🐛 Update dataset service for consistency
- 🐛 Update docker-compose.prod for consistency
- 🐛 Update docker-compose.prod.webhook for consistency
- 🐛 Update docker-compose.prod for consistency
- 🐛 Update docker-compose.dev for consistency
- 🐛 Update Docker image tag in CI workflow to match project name
- 🐛 Update database configuration in CI workflow for consistency
- 🐛 Update Docker image name in CI workflow to match project name
- 🐛 Update project name in devcontainer configuration
- 🐛 Update project description for accuracy
- 🐛 Update database configuration in .env.vagrant.example for consistency
- 🐛 Update database configuration in .env.local.example for consistency
- 🐛 Update environment variables in .env.docker.production.example for consistency
- 🐛 Update database configuration in .env.docker.example for consistency

### Refactor

- **tests**: 🔧 Simplify test client setup and clean up unused code

## 1.4.0 (2025-12-01)

### Feat

- ✨ Add database seeding command to entrypoint script

## 1.3.0 (2025-12-01)

### Feat

- ✨ Add database seeding step during deployment

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
