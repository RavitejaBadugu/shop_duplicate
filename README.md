# Shop Price Match Guarantee
The kaggle competition link: https://www.kaggle.com/competitions/shopee-product-matching

Finding near-duplicates in large datasets is an important problem for many online businesses. In Shopee's case, everyday users can upload their own images and write their own product descriptions, adding an extra layer of challenge. Your task is to identify which products have been posted repeatedly. The differences between related products may be subtle while photos of identical products may be wildly different!



## Documentation

GPU Training folder contains the code requried to run using GPU.
TPU Training folder contains the code which was ran in kaggle
environment using TPUs.
The reason for creating two folders is first I tried using GPUs but it
is taking long time and it was getting difficult to run the experiments
using GPUs. So, I shifted my work to TPUs. In the TPU code at the last 
you will find the experiments which I ran and what hyperparameters
where chosen at last.
After Training the submitted models got 0.62 Private Score(mean f1 score).
![Screenshot 2022-08-02 221336](https://user-images.githubusercontent.com/63113063/182428743-5435fc34-f69a-4f2e-964c-65ac51b84f97.png)

The deployment is done in aws where I created Infrastructure which
includes componenets as:
1) VPC
2) Public Subnets and Private Subnets
3) Network Load Balancers and Application Load Balancers
4) Auto Scaling with scheduled scaling
5) Vpc Endpoint
6) AWS RDS
7) AWS S3


![The AWS Architecture which I designed.](https://github.com/RavitejaBadugu/shop_duplicate/blob/new_develop/AWS/My%20first%20Arch.png)



## Tech Stack

**Client:** Streamlit

**Server:** Fastapi

**For Models Deployment:** TF Serving,MLflow

**DataBase:** Postgresql(AWS RDS)

**Deployment:** AWS,Terraform


## Demo

https://user-images.githubusercontent.com/63113063/182014889-bc0178cf-16c7-40f7-9f61-4c75065bbd33.mp4

