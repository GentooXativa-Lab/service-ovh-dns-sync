import ovh
import os

config = {
    "application_name": os.environ.get("OVH_APP_NAME"),
    "application_key": os.environ.get("OVH_APP_KEY"),
    "application_secret": os.environ.get("OVH_APP_SECRET"),
    "consumer_key": os.environ.get("OVH_APP_CONSUMERKEY"),
    "endpoint": os.environ.get("OVH_APP_ENDPOINT"),
    "ip_check_address": os.environ.get("OVH_IP_CHECK_ADDRESS", "https://ifconfig.ovh/"),
    "domains": os.environ.get("OVH_DOMAINS", "example.com"),
}

def getOvhClient():
    """
    Get an OVH client
    """
    client = ovh.Client(
        endpoint=config["endpoint"],
        application_key=config["application_key"],
        application_secret=config["application_secret"],
        consumer_key=config["consumer_key"]
    )
    return client

def getZoneId(client, domain):
    """
    Get the zone ID for a domain
    """
    zones = client.get("/domain/zone")
    for zone in zones:
        if zone == domain:
            return zone
    return None

def retrievePublicIP():
    """
    Retrieve the public IP address of the machine
    """
    import requests
    response = requests.get(config["ip_check_address"])
    # remove last character (new line)
    finalResponse = response.text[:-1]    
    return finalResponse

def main():
    client = getOvhClient()
    print("Connected to OVH API, checking records for domains: {}".format(config["domains"]))
    
    publicIP = retrievePublicIP()
    print("Public IP: {}".format(publicIP))

    for domain in config["domains"].split(" "):
        try:
            zoneId = getZoneId(client, domain)
            if zoneId is None:
                print("Zone not found for domain: {}".format(domain))
                continue

            records = client.get("/domain/zone/{}/record".format(zoneId))
            for recordId in records:
                try:
                    record = client.get("/domain/zone/{}/record/{}".format(zoneId, recordId))
                    if record["fieldType"] == "A":
                        if record["target"] != publicIP:
                            print("Updating record for domain: {} zone: {}".format(domain, zoneId))
                            # client.put("/domain/zone/{}/record/{}".format(zoneId, record["id"]), target=publicIP)
                        else:
                            print("Record for domain: {}.{} is up to date".format(record["subDomain"], domain))
                except ovh.exceptions.ResourceNotFoundError:
                    print("Record not found for domain: {}".format(domain))
        
        except ovh.exceptions.ResourceNotFoundError:        
            print("Zone not found for domain: {}".format(domain))
            exit(1)

if __name__ == "__main__":
    main()
