import os
import openai

client = openai.OpenAI(api_key=os.getenv("GEMINI_API_KEY"), base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
messages = [
    {
        'role': 'system',
        'content': """# Introduction\n\nYou are an AI researcher setting up experiments. Please propose meaningful evaluation metrics that will help analyze the
performance and characteristics of solutions for this research task.\n\n# Research idea\n\nYou are an ambitious AI researcher who is looking to publish a paper that will
contribute significantly to the field.\nYou have an idea and you want to conduct creative experiments to gain scientific insights.\nYour aim is to run experiments to    
gather sufficient results for a top conference paper.\nYour research idea:\n\n\nTitle:\nDisentangled Latent Representations for Interpretable and Effective Cross-Modal  
Hashing\nAbstract:\nCross-modal hashing is a critical technique for efficient retrieval across heterogeneous data modalities like images and text. Current deep
cross-modal hashing methods learn monolithic hash codes that compress all semantic information into a single binary vector. While effective for overall similarity       
search, this monolithic representation lacks interpretability and may struggle with fine-grained or multi-faceted queries. We hypothesize that learning a disentangled   
latent representation, where distinct dimensions or groups of dimensions correspond to separable semantic factors, before generating hash codes, can yield superior      
retrieval performance and provide valuable insights into the learned cross-modal space. This approach allows the model to explicitly learn and align different semantic  
aspects across modalities. We propose a novel Disentangled Cross-Modal Hashing (DCMH) framework that incorporates a disentanglement objective alongside standard hashing 
losses (similarity preservation, quantization). Experiments on benchmark datasets will compare DCMH against state-of-the-art CMH methods using standard retrieval metrics
(mAP, PR curves). Furthermore, we will analyze the learned disentangled space using disentanglement metrics and investigate the potential for factor-specific retrieval  
or interpretation, demonstrating the benefits of disentanglement beyond just improved mAP.\nShort Hypothesis:\nLearning a disentangled latent representation before      
generating binary hash codes can improve cross-modal hashing performance and interpretability by explicitly separating distinct semantic factors. This is crucial because
traditional cross-modal hashing methods learn monolithic hash codes that conflate various semantic aspects, potentially hindering fine-grained retrieval and robustness  
to noise in specific factors. Cross-modal hashing provides a unique setting to investigate this, as the goal is alignment in a low-dimensional Hamming space, where      
disentangling factors could reveal which aspects are shared and most discriminative. There are no simpler ways to achieve the benefits of disentanglement (explicit      
factor separation, potential interpretability) without directly incorporating disentanglement principles into the learning process.\n\n\nCurrent Main Stage:
initial_implementation\nSub-stage: 1 - preliminary\nSub-stage goals: \n                - Focus on getting basic working implementation\n                - Use a simple   
dataset\n                - Aim for basic functional correctness\n                - If you are given "Code To Use", you can directly use it as a starting point.\n\n#     
Instructions\n\n- Propose a single evaluation metric that would be useful for analyzing the performance of solutions for this research task.\n- Note: Validation loss    
will be tracked separately so you don\'t need to include it in your response.\n- Format your response as a list containing:\n- - name: The name of the metric\n- -       
maximize: Whether higher values are better (true/false)\n- - description: A brief explanation of what the metric measuresYour list should contain only one metric.\n\n"""  
    },
    {
        'role': 'user',
        'content': "do as your instructions say"
    }
]
completion = client.chat.completions.create(model="gemini-2.5-flash-preview-04-17", messages=messages, temperature=0.7, max_tokens=400, n=1)
print(completion)
import pdb; pdb.set_trace();