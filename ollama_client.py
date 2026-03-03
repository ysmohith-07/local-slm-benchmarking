import requests, time, psutil, os

def query_model(model_name, prompt, temperature=0.0):
    start = time.time()
    response = requests.post('http://localhost:11434/api/generate',
        json={
            'model': model_name,
            'prompt': prompt,
            'stream': False,
            'options': {'temperature': temperature}
        })
    elapsed = time.time() - start
    data = response.json()
    return {
        'response': data.get('response'),
        'latency_seconds': round(elapsed, 3),
        'tokens_per_second': round(data.get('eval_count', 0) / max(elapsed, 0.001), 2),
        'memory_mb': round(psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024, 2)
    }

