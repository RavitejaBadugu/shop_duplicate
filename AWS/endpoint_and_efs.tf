resource "aws_vpc_endpoint" "s3-connector" {
    service_name = "com.amazonaws.us-east-2.s3"
    vpc_id = data.aws_vpc.shop-vpc.id
    vpc_endpoint_type = "Gateway"
    auto_accept = true
    route_table_ids = [aws_route_table.fastapi-route-table.id]
    tags = {
      "Name" = "vpc-endpoint-fastapi"
    } 
}