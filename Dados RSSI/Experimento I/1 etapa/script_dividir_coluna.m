j = 1;
k = 1;
for i = 1:150
   if mod(i,2) == 1  
    vimp(j)= v(i);
    j = j +1;
   end
   if mod(i,2) == 0
       vpar(k)= v(i);
       k = k +1;
   end
end
vpar = transpose(vpar);
vimp = transpose(vimp);