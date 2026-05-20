from js import Response, JSON
import json

# Cloudflare looks for an entrypoint function named 'on_fetch'
async def on_fetch(request, env, ctx):
    # Determine the URL path requested
    url = request.url
    
    # Simple Router Implementation
    if "/api/predict" in url and request.method == "POST":
        try:
            # Parse incoming body parameters
            body_text = await request.text()
            data = json.loads(body_text)
            
            # Example: Interacting with your bound D1 Database 
            # (Accessible via the binding name defined in wrangler.json)
            # query = await env.DB.prepare("SELECT * FROM students WHERE Student_ID = ?").bind(data.get("student_id")).first()
            
            # Place your predictive execution here (using joblib/scikit-learn)
            prediction_result = {"status": "success", "dropout_risk": "Low"}
            
            return Response.new(
                json.dumps(prediction_result), 
                headers={"Content-Type": "application/json"}
            )
        except Exception as e:
            return Response.new(
                json.dumps({"error": str(e)}), 
                headers={"Content-Type": "application/json"},
                status=500
            )

    # Default fallback response
    fallback = {"message": "Student Dropout Prediction API Runtime Active"}
    return Response.new(
        json.dumps(fallback), 
        headers={"Content-Type": "application/json"}
    )