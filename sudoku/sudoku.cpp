#include<iostream>
#include<vector>
#include<fstream>
using namespace std;
 
void prn(vector<vector<int> > v){
 
for(int i=0;i<20;i++){
    cout<<"---";
}
cout<<endl;
 
for(int i=0;i<9;i++){
    for(int j=0;j<9;j++){
        cout<<v[i][j]<<" ";
    }
    cout<<endl;
}
 
}
 
int getindex(int i){
if(i<=2) return 0;
else if(i<=5) return 3;
else
    return 6;
 
}
 
 
int chk(vector<vector<int> > &v,int k,int i,int j){
for(int t=0;t<9;t++){
    if(v[k][t]==j || v[t][i]==j)
        return 0;
}
int x = getindex(k);
int y = getindex(i);
 
for(int m=x;m<x+3;m++){
    for(int n=y;n<y+3;n++){
        if(v[m][n]==j)
            return 0;
    }
}
v[k][i]=j;
return 1;
 
 
}
 
 
int play(vector<vector<int> > &v,int k){
if(k==9) return 1;
 
for(int i=0;i<9;i++){
    if(v[k][i]==0){
        for(int j=1;j<=9;j++){
            if(chk(v,k,i,j) && play(v,k))
                    return 1;
        }
                v[k][i]=0;
                return 0;
    }
}
 
if(play(v,k+1))
        return 1;
else
        return 0;
}
 
int main(){
int m,n;
vector<vector<int> >v(9,vector<int>(9,0));
ifstream file("data.txt");
 
for(int i=0;i<9;i++){
    for(int j=0;j<9;j++){
        file>>v[i][j];
    }
}
 
if(play(v,0)){
    prn(v);
}
else{
    cout<<"unsolved";
}
 
}
