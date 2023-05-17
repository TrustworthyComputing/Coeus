function silhouette(input_path, output_path, mode, imgs)
    
    files = dir(fullfile(input_path,'*.png'));
    L = length(files);

    if mode == "--i"
        for i=1:L
            name = sprintf('%d.png', i);
            I = imread(fullfile(input_path,name));
            I = imresize(I, [1000 1000]);
            red = I(:,:,1); green = I(:,:,2); blue = I(:,:,3);
            I_gray = rgb2gray(I);
            x = I(1,1,:);
            out = red>x(1,1)-5 & green>x(1,1)-5 & blue>x(1,1)-5;
            I_edge = edge(I_gray, 'canny');
    
            se = strel('disk',10);
            I_close = imclose(I_edge, se);
    
            I_fill = imfill(I_close, 'holes');

            I_final = I_fill - out;
    
            output_file = sprintf('silhouette%d.png', i);
            final_path = fullfile(output_path, output_file);
            imwrite(I_final, final_path);
    
        end
    elseif mode == "--v"
        v = VideoReader(input_path);
        num_frames = v.NumFrames;
        n = num_frames/str2double(imgs);
        n = round(n);
        for i = 1:1:str2double(imgs)
            frames = read(v, i * (n-1));
            imwrite(frames, strcat(int2str(i),".png"));
            filename = sprintf("%d.png", i);
            I = imread(filename);
            I = imresize(I, [1000 1000]);
            red = I(:,:,1); green = I(:,:,2); blue = I(:,:,3);
            x = I(1,1,:);
            out = red>x(1)-5 & green>x(2)-5 & blue>x(3)-5;
            I_gray = rgb2gray(I);
            I_edge = edge(I_gray, 'canny');
            
            se = strel('disk',10);
            I_close = imclose(I_edge, se);
            
            I_fill = imfill(I_close, 'holes');
            
            I_final = I_fill - out;
            
            name = sprintf("projection%d.png", i);
            loc = fullfile(output_path,name);
            
            imwrite(I_final, loc);
            
        end
        
    end
end

