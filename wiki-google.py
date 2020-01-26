"""
Created by Aaron Li
Made in Python
If you want to run the code please install the wikipedia API
Use code in terminal to install
$ pip install wikipedia


"""


import wikipedia as wk

import numpy as np

import pickle

from timeit import default_timer as timer
from scipy import linalg as LA



"""
Call the wikipedia API and return the page links of that page
The variable page_name represnts the page you are searching
"""
def PageLinks(page_name):
    page=wk.page(page_name)
    return page.links


"""
Store values will take the chosen page and find the amount of Links
Input parameters:
link_num is a int represents that amount of shared links to look at. 
For example the page Linear Algebra might have 400 page links but we only want to look at the first 200. So, link_num=200

page_name a string that is the page you are intrested in.
file_name a string for the name of the file

Function Description:

To do that it will needs 6 steps
1. Create an array that will hold the page_links of page_name based on link_num
2. Create the page links array that stores the page links from each link in page_links array inside variable wl
Example: If Original wikipedia page is Linear Algebra and Linear Algebra has a page link to Eigen Vectors,
We would then store the page links of Eigen Vectors wikipedia page
3. Create dictionary from wl and find each shared connection from orginal page and wl page links
Example: We would look through the Eigen Vector page link and find all the pages that both Linear Algebra and Eigen Vector both share.
The two pages could of links like matrix, Gram-Schdmit, QR factorization in common. And therefore have 3 shared links
4. Store the location of the shared links in the locations array relative to the orginal page.
Example: The page link "matrix" could be the 7th page link on the Linear Algebra so we need to store that position in the location array
5. Append the to the value array a tuple with 3 fields (shared_links,fos_links[pos], fos_link[i])
    Shared_links represents the total number of shared_links 
    fos_link[pos] represents the specific shared link between the orginal page and shared link page
    fos_link[i] represents the the shared link page
    Example: The Linear Algebra Page and Eigen Vector page appen array would look like this:
    values=[(3,"matrix","eigen vectors"),(3,"Gram-Schdmit","eigen vectors"),(3,"QR factorization","eigen vectors")]
6. After looping through all the links pickle the values array
"""
def StoreValues(link_num,page_name,file_name):
    start=timer()
    values=[] # Stores a tuple that holds the following total shared links, specific shared link, and original web page link
    locations=[] # Stores the location of the shared link between orignal web page and the shared link web page
    shared_links=np.array(PageLinks(page_name)[0:link_num])
    link_size=shared_links.size

    for i in range(link_size):
        shared_link_page=shared_links[i]
        try: 
            wl= wk.page(shared_link_page).links
        except wk.exceptions.DisambiguationError as e: #If unable to find wikipedia page throw out the data and go to next page
            continue 
        web_links=wl[0:link_num]
        link_dict= {link:0 for link in web_links if link!= shared_link_page} # Create a dictionary for the link to the fossil and exclude links that includes itself

        for link in shared_links: #Step 3 of Function description
            if link in link_dict.keys():
                link_dict[link]=1
                locations.append(np.where(shared_links==link)[0][0]) #Step 4 of function description
        shared_links_total= sum(link_dict.values())

        if shared_links_total==0: # No shared links then continue
            continue
        else:
            for pos in locations:
                values.append((shared_links_total,shared_links[pos],shared_links[i])) #Step 5 of function description
        link_dict={}
        locations=[]
    end=timer()

    with open(file_name, 'wb') as fp:
        pickle.dump(values,fp)
    print('The time ellasped is ', end-start)




"""
Create the Probaility Transistion Matrix
Input parameters:
file_name a string the name of the text file with values  stored in it from StoreValues.

Function description:


    1.  Checks to make sure the shared links is inside the web of shared links (i.e shared_links[i]) 
    meaning if any of the shared links in the orignal shared links web did not connect ot any other links we toss them out.
    Ex: In page Linear algebra. Eigen vector and Linear Algebra Link might both link to fossils but fossil might have 0 shared links.
    We then throw out fossils and we do not include it in our  Probability Transistion Matrix
    2. Count up all instances of the link being linked to anther page
    3. Divide 1 by the sum of the total amount of links and place that value into the correct position
    4. Save Probility transistion matrix as eigen_mat.txt

"""
def CreateMatrix(file_name):
    with open(file_name, 'rb') as fp: #Unpickle the values data 
        values=pickle.load(fp)
    web_links=[1] #intialize to seperate arrays and check to make sure they have the proper 
    web_links_cleaned=[]
    actual_values=values
    while len(web_links)-len(web_links_cleaned)!=0: #Ensure that each shared links is is connect to the web of shared links
        print("iterating!", len(web_links), len(web_links_cleaned))
        web_links= [link for val,check,link in actual_values]
        tmp= actual_values
        actual_values=[] 

        for val,check,link in tmp:
            if check in web_links: #Only append if shared link is in shared page web
                actual_values.append((val,check,link))
        web_links_cleaned=[link for val,check,link in actual_values]

    unique_links=set(web_links_cleaned) # Grab only unique links
    unique_links=np.array(list(unique_links))
    mat_size=len(unique_links)
    mat=np.zeros((mat_size, mat_size))
    links_dict={l:0 for l in unique_links}


    for l in web_links_cleaned: # Function description 2
        links_dict[l]+=1

    tmp="null"
    for val,check,link in actual_values:
        if tmp!= link: # Go to a differnt position in matrix when link is no longer the same
            link_pos=np.where(unique_links==link)[0][0]
            tmp=link
        location=np.where(unique_links==check)[0][0]
        mat[location,link_pos] = 1.0/links_dict[link]
    np.savetxt('eigen_mat.txt',mat,)
    return unique_links


""" Matrix operations definition"""
def importance(ei_mat):
    evals,evecs= np.linalg.eig(ei_mat)
    return evals



"""
PMCT (Power Method Convergence Theorem)
Input paramters:
amt is an int that represents the amount of matrix multiplication iterations
mat is the eigen matrix
num_links is the amount of page_links is the web

Continue to multiply the Probability Transistion matrix by itself 
The comlumn wise columns will stablize and then we divide the number by 1/num_links

returns the importance/singular values ordered and not ordered

"""
def PMCT(amt, mat, num_links):
    start=timer()
    original=mat
    z= 1.0/num_links

    for i in range(amt):
        mat= np.matmul(mat,original)

    sing=np.sum(mat, axis=1)*z # Sum row wise Divide by z value to get the importance
    sort_sing=np.sort(sing)[::-1] #Want the ordering to be greatest to smallest
    end=timer()
    print('The time ellasped in PMCT is', end-start)
    return sing, sort_sing

"""
GuassElim (Guassian Elimination)
Input paramater:
eigen_mat is the Probability Transition Matrix

Finds the eigen vector assoicated the the eigen value of one
Takes the eigen vector and divides each value by the sum 

returns the importance/singular values ordered and not ordered

"""
def GuassElim(eigen_mat):
    start=timer()
    np.fill_diagonal(eigen_mat, -1.0)
    
    sing= LA.null_space(eigen_mat)

    sing=[val[0] for val in sing] #Currently a each singular value is a it's own list so we need to change
    sing= np.array(sing)

    sing_sum=sum(sing)
    sing=sing/sing_sum
    
    sort_sing=np.sort(sing)[::-1] #Change the order for ascending to descending
    end=timer()
    print('The time ellasped in Guassian Elimination is ', end-start)
    return sing, sort_sing



"""
BFPT (Banach Fixed Point Theorem) The fastest method
Input paramater:
amt an int that is an iterator
eigen_mat is the Probability Transition Matrix
B  a dampening factor that also accounts for random sinks 


Finds the singular values with by first created a vector pf 1/(num of web page links)
Then iterates the singular vector by taking the dot product of the eigen_mat and the old singular vector

returns the importance/singular values ordered and not ordered

"""
def BFPT(amt, eigen_mat, B):
    start=timer()
    X_0 = np.ones_like(eigen_mat[0])/len(eigen_mat[0])
    sing= np.copy(X_0)
    for i in range(amt):
        sing=((1-B)*np.dot(eigen_mat,sing)+ B*X_0)
    sort_sing=np.sort(sing)[::-1] #Change the order for ascending to descending
    end=timer()
    print('The time ellasped in method BFPT is ', end-start)
    return sing, sort_sing



def print_results(sing,sort_sing,links):
    for i in range(8):
        pos=np.where(sing==sort_sing[i])[0][0]
        print(links[pos])
    pos_last= np.where(sing==sort_sing[-1])[0][0]
    print(sort_sing[-1])
    print("Least relevant is ", links[pos_last])



def main():

    val_name="values.txt"
    #StoreValues(50,"Linear algebra", val_name) #Uncomment store values if you want to create a new values.txt
    fos_links=CreateMatrix(val_name)

    with open("eigen_mat.txt") as f:
        eigen_mat= [[float(num) for num in line.split(' ')] for line in f]

    link_num=len(eigen_mat)

    eigen_mat=np.reshape(np.array(eigen_mat),(link_num,link_num))


    sing,sort_sing=PMCT(60, eigen_mat,link_num)

    sing,sort_sing=GuassElim(eigen_mat)

    sing,sort_sing= BFPT(60,eigen_mat,0)


    print_results(sing,sort_sing, fos_links)

    return

main()
