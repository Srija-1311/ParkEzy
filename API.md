# API Documentation

REST API documentation for the Smart Parking System.

## Base URL

```
http://localhost:5000
```

## Endpoints

### 1. Get Main Interface

**Endpoint:** `GET /`

**Description:** Returns the main web interface HTML page.

**Response:**
- Content-Type: `text/html`
- Status: `200 OK`

**Example:**
```bash
curl http://localhost:5000/
```

---

### 2. Detect Parking Occupancy

**Endpoint:** `POST /detect`

**Description:** Upload an image and detect parking space occupancy.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body Parameters:
  - `image` (file, required): Image file (jpg, jpeg, png)

**Response:**

Success (200 OK):
```json
{
  "success": true,
  "image_path": "static/uploads/parking_lot.jpg",
  "total_slots": 100,
  "occupied": 45,
  "vacant": 55,
  "occupancy_rate": 45.0
}
```

Error (400 Bad Request):
```json
{
  "error": "No image file provided"
}
```

Error (413 Payload Too Large):
```json
{
  "error": "File too large. Maximum size is 16MB"
}
```

Error (500 Internal Server Error):
```json
{
  "error": "Processing failed: [error message]"
}
```

**Example using cURL:**
```bash
curl -X POST \
  -F "image=@parking_lot.jpg" \
  http://localhost:5000/detect
```

**Example using Python:**
```python
import requests

url = "http://localhost:5000/detect"
files = {"image": open("parking_lot.jpg", "rb")}

response = requests.post(url, files=files)
data = response.json()

print(f"Total Slots: {data['total_slots']}")
print(f"Occupied: {data['occupied']}")
print(f"Vacant: {data['vacant']}")
print(f"Occupancy Rate: {data['occupancy_rate']}%")
```

**Example using JavaScript:**
```javascript
const formData = new FormData();
formData.append('image', fileInput.files[0]);

fetch('http://localhost:5000/detect', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('Total Slots:', data.total_slots);
  console.log('Occupied:', data.occupied);
  console.log('Vacant:', data.vacant);
  console.log('Occupancy Rate:', data.occupancy_rate + '%');
})
.catch(error => console.error('Error:', error));
```

---

## Response Fields

### Detection Response

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether detection was successful |
| `image_path` | string | Path to processed image with annotations |
| `total_slots` | integer | Total number of parking slots |
| `occupied` | integer | Number of occupied slots |
| `vacant` | integer | Number of vacant slots |
| `occupancy_rate` | float | Percentage of occupied slots (0-100) |

### Error Response

| Field | Type | Description |
|-------|------|-------------|
| `error` | string | Error message describing what went wrong |

---

## Status Codes

| Code | Description |
|------|-------------|
| 200 | Success - Request processed successfully |
| 400 | Bad Request - Invalid input or missing parameters |
| 413 | Payload Too Large - File exceeds maximum size |
| 500 | Internal Server Error - Processing failed |

---

## File Upload Constraints

- **Allowed formats:** JPG, JPEG, PNG
- **Maximum file size:** 16 MB
- **Recommended resolution:** 640x480 to 1920x1080

---

## Rate Limiting

Currently, no rate limiting is implemented. For production use, consider implementing rate limiting to prevent abuse.

**Recommended limits:**
- 10 requests per minute per IP
- 100 requests per hour per IP

---

## Error Handling

### Common Errors

1. **No image file provided**
   - Cause: Request missing image file
   - Solution: Include image in form data

2. **Invalid file type**
   - Cause: File extension not allowed
   - Solution: Use JPG, JPEG, or PNG format

3. **File too large**
   - Cause: File exceeds 16MB limit
   - Solution: Compress or resize image

4. **Failed to read image**
   - Cause: Corrupted or invalid image file
   - Solution: Verify image file integrity

5. **Processing failed**
   - Cause: Internal error during detection
   - Solution: Check server logs for details

---

## Integration Examples

### Python Integration

```python
import requests
import json

class ParkingDetector:
    def __init__(self, api_url="http://localhost:5000"):
        self.api_url = api_url
    
    def detect(self, image_path):
        """Detect parking occupancy in image"""
        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = requests.post(
                f"{self.api_url}/detect",
                files=files
            )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.json().get('error')}")

# Usage
detector = ParkingDetector()
result = detector.detect("parking_lot.jpg")
print(f"Occupancy: {result['occupancy_rate']}%")
```

### Node.js Integration

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

async function detectParking(imagePath) {
  const form = new FormData();
  form.append('image', fs.createReadStream(imagePath));
  
  try {
    const response = await axios.post(
      'http://localhost:5000/detect',
      form,
      { headers: form.getHeaders() }
    );
    
    return response.data;
  } catch (error) {
    throw new Error(error.response.data.error);
  }
}

// Usage
detectParking('parking_lot.jpg')
  .then(result => {
    console.log(`Occupancy: ${result.occupancy_rate}%`);
  })
  .catch(error => {
    console.error('Error:', error.message);
  });
```

---

## WebSocket Support

Currently not implemented. For real-time updates, consider polling the API or implementing WebSocket support for live camera feeds.

---

## Authentication

Currently not implemented. For production use, consider adding:
- API key authentication
- OAuth 2.0
- JWT tokens

---

## Versioning

Current API version: v1 (implicit)

Future versions may include explicit versioning:
- `/api/v1/detect`
- `/api/v2/detect`

---

## Support

For API issues or questions:
- Check server logs
- Review error messages
- Consult main documentation
