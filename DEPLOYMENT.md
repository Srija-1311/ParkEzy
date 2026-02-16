# Deployment Guide

Guide for deploying the Smart Parking System to production.

## Pre-Deployment Checklist

- [ ] All tests pass (`python test_system.py`)
- [ ] Environment variables configured
- [ ] Secret key set for production
- [ ] Model files available
- [ ] Slots JSON file available
- [ ] Upload directory writable
- [ ] Dependencies installed

## Environment Variables

Create a `.env` file (use `.env.example` as template):

```bash
FLASK_ENV=production
SECRET_KEY=your-secure-random-secret-key
DEBUG=False
HOST=0.0.0.0
PORT=5000
```

## Production Setup

### 1. Install Production Dependencies

```bash
pip install -r requirements.txt
pip install gunicorn  # WSGI server
```

### 2. Configure Application

Edit `config.py` to ensure production settings are correct.

### 3. Run with Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Options:
- `-w 4`: 4 worker processes
- `-b 0.0.0.0:5000`: Bind to all interfaces on port 5000
- `--timeout 120`: Increase timeout for large images

### 4. Use Nginx as Reverse Proxy

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /path/to/smart-parking-system/static;
        expires 30d;
    }
}
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy application
COPY . .

# Create uploads directory
RUN mkdir -p static/uploads

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "120", "app:app"]
```

### Build and Run

```bash
docker build -t smart-parking-system .
docker run -p 5000:5000 -v $(pwd)/static/uploads:/app/static/uploads smart-parking-system
```

## Cloud Deployment

### AWS Elastic Beanstalk

1. Install EB CLI: `pip install awsebcli`
2. Initialize: `eb init`
3. Create environment: `eb create production`
4. Deploy: `eb deploy`

### Heroku

1. Create `Procfile`:
```
web: gunicorn app:app
```

2. Deploy:
```bash
heroku create your-app-name
git push heroku main
```

### Google Cloud Run

1. Build container:
```bash
gcloud builds submit --tag gcr.io/PROJECT-ID/smart-parking
```

2. Deploy:
```bash
gcloud run deploy --image gcr.io/PROJECT-ID/smart-parking --platform managed
```

## Performance Optimization

### 1. Model Optimization
- Use YOLOv8n (nano) for faster inference
- Consider quantization for edge deployment

### 2. Caching
- Cache model in memory (already implemented)
- Cache slots data (already implemented)

### 3. Image Processing
- Resize large images before processing
- Implement async processing for multiple uploads

### 4. Load Balancing
- Use multiple Gunicorn workers
- Deploy behind load balancer for high traffic

## Monitoring

### Application Logs

```bash
# View logs
tail -f /var/log/smart-parking/app.log

# With Gunicorn
gunicorn --access-logfile - --error-logfile - app:app
```

### Health Check Endpoint

Add to `app.py`:

```python
@app.route('/health')
def health():
    return {'status': 'healthy'}, 200
```

## Security Considerations

1. **Secret Key**: Use strong random secret key
2. **File Upload**: Validate file types and sizes (already implemented)
3. **HTTPS**: Use SSL/TLS in production
4. **Rate Limiting**: Implement rate limiting for API endpoints
5. **CORS**: Configure CORS if needed for API access

## Backup Strategy

1. **Model Files**: Keep backup of trained models
2. **Slots Data**: Version control slots.json
3. **Uploads**: Regular cleanup or backup of uploaded images

## Troubleshooting

### High Memory Usage
- Reduce number of workers
- Implement request queuing
- Use smaller model variant

### Slow Processing
- Optimize image size
- Use GPU if available
- Implement caching

### Upload Failures
- Check disk space
- Verify upload directory permissions
- Check file size limits

## Maintenance

### Regular Tasks
- Clear old uploaded images
- Monitor disk usage
- Update dependencies
- Review logs for errors

### Updates
```bash
git pull origin main
pip install -r requirements.txt
sudo systemctl restart smart-parking
```

## Support

For deployment issues, check:
- Application logs
- System logs
- Network connectivity
- File permissions
