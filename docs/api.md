# API Documentation

## Base URL
All API endpoints are prefixed with `/api`

Example: `http://localhost:8000/api/images`

## Common Endpoints

These endpoints are available for all modules:

### Health Check
```
GET /api/health
```
Returns system health status and available modules.

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "modules": ["classifier", "matcher", "viewer", "cluster", "shop", "text_labeler"]
}
```

### Load Settings
```
GET /api/load_settings
```
Load user preferences for the current module.

**Response:**
```json
{
  "settings": {
    "lastPage": 5,
    "viewMode": "grid",
    "imageMode": true
  }
}
```

### Save Settings
```
POST /api/save_settings
```
Save user preferences for the current module.

**Request Body:**
```json
{
  "lastPage": 5,
  "viewMode": "grid",
  "imageMode": true
}
```

**Response:**
```json
{
  "success": true
}
```

## Text Labeler Endpoints

### Get Images (Paginated)
```
GET /api/images?page=0
```
Get a paginated list of images with their labels.

**Query Parameters:**
- `page` (int, default=0): Page number (0-indexed)

**Response:**
```json
{
  "images": [
    {
      "image": "path/to/image1.jpg",
      "text": "A cat sitting on a chair"
    },
    {
      "image": "path/to/image2.jpg",
      "text": ""
    }
  ],
  "total_pages": 10,
  "current_page": 0
}
```

### Update Image Text
```
POST /api/images/update
```
Update the text label for a specific image.

**Request Body:**
```json
{
  "path": "path/to/image1.jpg",
  "text": "Updated label text"
}
```

**Response:**
```json
{
  "success": true
}
```

**Error Response (404):**
```json
{
  "detail": "Image not found in dataset: path/to/image1.jpg"
}
```

### Sync Page
```
POST /api/sync_page
```
Force save all changes for the current page.

**Request Body:**
```json
{
  "page": 0
}
```

**Response:**
```json
{
  "success": true
}
```

### Get Image File
```
GET /api/images/file?image_path=path/to/image.jpg
```
Serve an image file from the filesystem.

**Query Parameters:**
- `image_path` (string, required): Path to the image file

**Response:** Image file (JPEG/PNG/etc.)

### Reload Dataset
```
POST /api/reload
```
Reload the JSONL dataset from disk (useful if modified externally).

**Response:**
```json
{
  "success": true,
  "items_loaded": 1000
}
```

### Get Statistics
```
GET /api/stats
```
Get dataset statistics.

**Response:**
```json
{
  "total_items": 1000,
  "labeled": 750,
  "unlabeled": 250,
  "labeled_percentage": 75.0
}
```

## Classifier Endpoints

### Get Images (Paginated)
```
GET /api/images?page=0
```
Get a paginated list of images for classification.

**Response:**
```json
{
  "images": [...],
  "total_pages": 10,
  "current_page": 0,
  "selected_images": {
    "image1.jpg": "status1",
    "image2.jpg": "status2"
  },
  "statuses": ["", "keep", "delete", "review"]
}
```

### Get Groups
```
GET /api/groups?page=0
```
Get images grouped by cluster.

**Response:** Similar to Get Images

### Get Selected Images
```
GET /api/images/selected
```
Get all classified/selected images.

**Response:**
```json
{
  "images": [...],
  "selected_images": {...}
}
```

### Update Image Classification
```
POST /api/images/update
```
Update classification status for an image.

**Request Body:**
```json
{
  "path": "path/to/image.jpg",
  "status": "keep"
}
```

### Sync Classifications
```
POST /api/sync_classifications
```
Save all classifications to disk.

## Matcher Endpoints

### Get Matching Pairs
```
GET /api/images?page=0
```
Get paginated source-target matching pairs.

**Response:**
```json
{
  "images": [
    {
      "id": "0",
      "source_name": "Product A",
      "source_image": "path/to/source.jpg",
      "target_name": "Product B",
      "target_image": "path/to/target.jpg",
      "matching": true
    }
  ],
  "total_pages": 10,
  "current_page": 0
}
```

### Update Match
```
POST /api/images/update
```
Update match status for a pair.

**Request Body:**
```json
{
  "id": "0",
  "source_name": "Product A",
  "source_image": "path/to/source.jpg",
  "target_name": "Product B",
  "target_image": "path/to/target.jpg",
  "matching": true
}
```

### Sync Changes
```
POST /api/sync_changes
```
Save accumulated matching decisions.

### Sync Page
```
POST /api/sync_page
```
Save current page of matches.

**Request Body:**
```json
{
  "page": 0
}
```

### Sync All
```
POST /api/sync_all
```
Save all matching data.

## Viewer Endpoints

### Get Images with Similarities
```
GET /api/images?page=0
```
Get images with their nearest neighbors.

**Response:**
```json
{
  "images": [
    {
      "name": "image1.jpg",
      "path": "path/to/image1.jpg",
      "rn18_l2": "path/to/similar1.jpg",
      "rn18_l2_d": 0.15,
      "rn18_ip": "path/to/similar2.jpg",
      "rn18_ip_d": 0.92
    }
  ],
  "total_pages": 10,
  "current_page": 0
}
```

### Sync Page
```
POST /api/sync_page
```
Save current page data.

## Cluster Endpoints

### Get Clustered Images
```
GET /api/images?page=0
```
Get images grouped by cluster ID.

**Response:**
```json
{
  "images": [
    {
      "id": "0",
      "name": "image1.jpg",
      "path": "path/to/image1.jpg",
      "cluster_id": 5,
      "path_id": "https://example.com/image1.jpg"
    }
  ],
  "total_pages": 10,
  "current_page": 0
}
```

### Proxy Image
```
GET /api/proxy-image?url=https://example.com/image.jpg
```
Proxy external images to avoid CORS issues.

**Response:** Image file with caching headers

## Shop Endpoints

### Get Product Matches
```
GET /api/images?page=0
```
Get crawler products with reference recommendations.

**Response:**
```json
{
  "images": [
    {
      "id": 123,
      "cp_name": "Product A",
      "cp_image": "https://cdn.example.com/a.jpg",
      "ref_pid": 456,
      "ref_name": "Reference Product A",
      "ref_image": "https://cdn.example.com/ref_a.jpg",
      "recom_ref_pid": 789,
      "recom_ref_name": "Recommended Product",
      "recom_ref_image": "https://cdn.example.com/recom.jpg"
    }
  ],
  "total_pages": 10,
  "current_page": 0
}
```

### Update Product Reference
```
POST /api/images/update
```
Update a crawler product's reference.

**Request Body:**
```json
{
  "id": 123,
  "ref_pid": 789
}
```

### Proxy Image
```
GET /api/proxy-image?url=https://cdn.example.com/image.jpg
```
Proxy CDN images.

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid image path"
}
```

### 404 Not Found
```json
{
  "detail": "Image not found in dataset: path/to/image.jpg"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to save changes: [error details]"
}
```

## Rate Limiting

Currently, there are no rate limits implemented. For production use, consider adding rate limiting middleware.

## Authentication

Currently, no authentication is required. For production use, consider adding:
- API key authentication
- OAuth 2.0
- JWT tokens

## Pagination

All paginated endpoints follow this pattern:
- Pages are 0-indexed
- Default page size is 100 (configurable via environment variables)
- Page size cannot be changed via API (set in configuration)

## Caching

Images served via `/api/images/file` and `/api/proxy-image` include cache headers:
```
Cache-Control: public, max-age=86400
```
This caches images for 24 hours.

## WebSocket Support

Currently not implemented. Future versions may include WebSocket support for:
- Real-time collaboration
- Live progress updates
- Batch operation status

## Versioning

Current API version: 2.0.0

Future versions will maintain backward compatibility or use versioned endpoints:
```
/api/v2/images
```
