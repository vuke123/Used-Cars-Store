from apps.core.logger import Logger
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from apps.core.file_operation import FileOperation
from kneed import KneeLocator

class KMeansCluster:
    def __init__(self,run_id):
        self.run_id = run_id
        self.logger = Logger(self.run_id, 'KMeansCluster', 'training')
        self.fileOperation = FileOperation(self.run_id, 'training')

    def elbow_plot(self,data):
        wcss=[]
        try:
            self.logger.info('Start of elbow plotting...')
            for i in range (1,11):
                kmeans=KMeans(n_clusters=i,init='k-means++',random_state=0)
                kmeans.fit(data)
                wcss.append(kmeans.inertia_)
            plt.plot(range(1,11),wcss)
            plt.title('The Elbow Method')
            plt.xlabel('Number of clusters')
            plt.ylabel('WCSS')
            #plt.show()
            plt.savefig('apps/models/kmeans_elbow.png')
            self.kn = KneeLocator(range(1, 11), wcss, curve='convex', direction='decreasing')
            self.logger.info('The optimum number of clusters is: '+str(self.kn.knee))
            self.logger.info('End of elbow plotting...')
            return self.kn.knee

        except Exception as e:
            self.logger.exception('Exception raised while elbow plotting:' + str(e))
            raise Exception()

    def create_clusters(self,data,number_of_clusters):
        self.data=data
        try:
            self.logger.info('Start of Create clusters...')
            self.kmeans = KMeans(n_clusters=number_of_clusters, init='k-means++', random_state=0)
            self.y_kmeans=self.kmeans.fit_predict(data)
            self.saveModel = self.fileOperation.save_model(self.kmeans, 'KMeans')
            self.data['Cluster']=self.y_kmeans
            self.logger.info('succesfully created '+str(self.kn.knee)+ 'clusters.')
            self.logger.info('End of Create clusters...')
            return self.data
        except Exception as e:
            self.logger.exception('Exception raised while Creating clusters:' + str(e))
            raise Exception()