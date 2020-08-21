# provenance-holder
## Startup-Guide
#### Getting the Prototype on Your Machine
There are two simple steps in order to get the prototype on your local machine. First, navigate to the directory where you wish to save the repository. Next, enter the following command in your terminal: `git clone https://github.com/karlo-mirkovic/provenance-holder.git`

#### Requirements
Firstly, in order to run the prototype properly and begin testing the mock-up implementation, the machine needs to have several requirements, in the form of installations, satisfied.
* python3
* sqlalchemy
* postgres
* ed25519

On a macOS, the installation of these requirements is very simple.
1. Place the list of requirements in a `requirements.txt` file
2. Open a terminal
3. Go to directory
4. Run `pip3 install -r requirements.txt`

Once the dependencies have been installed, the machine is ready to test the provenance-holder prototype.
#### Testing
Most of the testing of the prototype is done through the `src/util.py` and `src/provenanceholder.py` python files. The `util.py` python file contains a python method that fills the database with 8 provenance entries, namely 4 adaptations and 4 executions. In `provenanceholder.py`, within the main method, the `fill_dummy` method is called and the database is filled. Further, two users are created and added to the controller database for testing purposes. Lastly, two query entries are created, one of each type supported by the current version of the Provenance Holder.

To whether the retrieve and collect operations work, one can invoke the adapter collect and retrieve methods and let the Provenance Holder handle the operation.
To invoke and view the results, use the following code snippet at the bottom of `provenanceholder.py`
```python
results_1 = provenance_holder.adapter.retrieve(query_entry_1, provenance_holder, 'execution')
results_2 = provenance_holder.adapter.retrieve(query_entry_2, provenance_holder, 'adaptation')

for r in results_1:
  print(r)
  
print()

for r in results_2:
  print(r)
```
If results contains the correct database enrties, both the storing and retrieval of the data is functional.
Furthermore, if you wish to query the database with different parameters, simply change the values of the atributes in `query_entry_1` or `query_entry_2`

#### ActiveMQ
To test the ActiveMQ functionality, you need to have activemq installed and running. After this, the code in `connect_to_activemq.py` can be used. Simply modify the `conn.send` line with parameters you wish to send ro verify that the connection is established. The files in the `messages` directory are meant for testing, however, there is no parser implemented. In the case of using a third party parser, simply modify the files in that directory adequately and send them via STOMP and ActiveMQ to the `messageQueue` destination.
